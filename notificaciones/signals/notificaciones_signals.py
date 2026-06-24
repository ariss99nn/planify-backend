# notificaciones/signals/notificaciones_signals.py
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

logger = logging.getLogger(__name__)

_MANAGERS_GROUP = 'alertas_managers'


def _ws_dispatch(channel_layer, group: str, message: dict) -> None:
    from asgiref.sync import async_to_sync
    try:
        async_to_sync(channel_layer.group_send)(group, message)
    except Exception as exc:
        logger.error("WS group_send '%s' falló: %s", group, exc)


def _build_nueva_payload(instance) -> dict:
    from notificaciones.serializers.notificaciones_serializer import AlertaWSPayloadSerializer
    data = AlertaWSPayloadSerializer(instance).data
    return {'type': 'alerta_nueva', **data}


def _build_conflicto_payload(instance) -> dict:
    return {
        'type':        'alerta_conflicto',
        'descripcion': instance.descripcion,
        'bloque_id':   instance.bloque_origen_id,
        'fecha':       instance.fecha_creacion.isoformat(),
    }


def _crear_notificacion(instance) -> None:
    """
    Crea el registro Notificacion asociado a la Alerta.
    Usa update_or_create para ser idempotente y evitar
    IntegrityError en condiciones de carrera (race condition
    entre dos workers creando la misma alerta a la vez).
    """
    from notificaciones.models.notificaciones_model import Notificacion

    if not instance.destinatario_id:
        return

    canal_map = {
        'EMAIL': Notificacion.Canal.EMAIL,
        'SMS':   Notificacion.Canal.SMS,
        'APP':   Notificacion.Canal.APP,
    }
    canal = canal_map.get(instance.formato_alerta, Notificacion.Canal.APP)

    try:
        Notificacion.objects.get_or_create(
            alerta=instance,
            destinatario_id=instance.destinatario_id,
            canal=canal,
            defaults={'estado': Notificacion.Estado.PENDIENTE},
        )
    except Exception as exc:
        # En el caso muy raro de race condition que escape al get_or_create,
        # logueamos y seguimos — no rompemos el flujo principal.
        logger.warning(
            "No se pudo crear Notificacion para alerta %s: %s",
            instance.pk, exc,
        )


@receiver(post_save, sender='alertas.Alerta')
def enviar_alerta_websocket(sender, instance, created, **kwargs) -> None:
    """
    Dispara tras cada Alerta guardada individualmente.
    — Crea el registro Notificacion.
    — Despacha el mensaje WebSocket dentro de on_commit.

    bulk_create no dispara post_save. Los puntos que usan bulk_create
    deben llamar dispatch_alertas_bulk() manualmente.
    """
    if not created:
        return

    _crear_notificacion(instance)

    from channels.layers import get_channel_layer
    from alertas.models.alerta_model import Alerta

    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.warning("Channel layer no configurado — WS omitido para alerta %s", instance.pk)
        return

    def _dispatch():
        if instance.destinatario_id:
            _ws_dispatch(
                channel_layer,
                f'alertas_user_{instance.destinatario_id}',
                _build_nueva_payload(instance),
            )
        if instance.tipo == Alerta.TipoAlerta.CONFLICTO:
            _ws_dispatch(
                channel_layer,
                _MANAGERS_GROUP,
                _build_conflicto_payload(instance),
            )

    transaction.on_commit(_dispatch)


def dispatch_alertas_bulk(alertas: list) -> None:
    """
    Despacha WS y crea Notificaciones para alertas creadas con bulk_create.

    Garantiza que las alertas tengan PK asignado antes de procesar.
    En MySQL/SQLite antiguo bulk_create puede no devolver PKs;
    en ese caso recargamos desde DB por (tipo, destinatario, bloque_origen).

    Uso:
        alertas = Alerta.objects.bulk_create([...])
        dispatch_alertas_bulk(alertas)
    """
    from channels.layers import get_channel_layer
    from alertas.models.alerta_model import Alerta

    # Garantizar PKs — crítico para _crear_notificacion y el payload WS
    alertas_con_pk = []
    sin_pk = []
    for a in alertas:
        if a.pk:
            alertas_con_pk.append(a)
        else:
            sin_pk.append(a)

    if sin_pk:
        # Fallback: recargar desde DB los que no tienen PK
        # Esto ocurre en MySQL < 8 y SQLite sin returning
        logger.warning(
            "bulk_create devolvió %d alertas sin PK — recargando desde DB",
            len(sin_pk),
        )
        from django.db.models import Q
        import functools
        q = functools.reduce(
            lambda acc, a: acc | Q(
                destinatario_id=a.destinatario_id,
                tipo=a.tipo,
                bloque_origen_id=a.bloque_origen_id,
            ),
            sin_pk,
            Q(),
        )
        alertas_con_pk += list(Alerta.objects.filter(q).order_by('-fecha_creacion')[:len(sin_pk)])

    channel_layer = get_channel_layer()

    def _commit():
        for instance in alertas_con_pk:
            _crear_notificacion(instance)
        if channel_layer is None:
            return
        for instance in alertas_con_pk:
            if instance.destinatario_id:
                _ws_dispatch(
                    channel_layer,
                    f'alertas_user_{instance.destinatario_id}',
                    _build_nueva_payload(instance),
                )
            if instance.tipo == Alerta.TipoAlerta.CONFLICTO:
                _ws_dispatch(
                    channel_layer,
                    _MANAGERS_GROUP,
                    _build_conflicto_payload(instance),
                )

    transaction.on_commit(_commit)