# alertas/signals/alertas_signals.py
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender='bhorario.BloqueHorario')
def detectar_conflictos_horario(sender, instance, created, **kwargs) -> None:
    """
    Al crear un BloqueHorario detecta solapamientos y genera alertas
    consolidadas para el docente y para todos los gestores activos.

    El despacho WebSocket y la creación de Notificacion quedan delegados
    a notificaciones.signals, que escucha post_save de Alerta.
    Las alertas bulk se despachan manualmente con dispatch_alertas_bulk.
    """
    if not created or not instance.docente_id:
        return

    from alertas.models.alerta_model import Alerta
    from notificaciones.signals.notificaciones_signals import dispatch_alertas_bulk
    from users.models.user import User

    from bhorario.models.bloque_horario_model import BloqueHorario

    conflictos_list = list(BloqueHorario.objects.filter(
        dia_semana=instance.dia_semana,
        docente=instance.docente,
        hora_inicio__lt=instance.hora_fin,
        hora_fin__gt=instance.hora_inicio,
    ).exclude(pk=instance.pk))
    if not conflictos_list:
        return
    ids_conflicto = ', '.join(str(c.pk) for c in conflictos_list)
    
    descripcion_base = (
        f"Conflicto de horario: el docente {instance.docente} "
        f"tiene bloques solapados el {instance.get_dia_semana_display()} "
        f"{instance.hora_inicio:%H:%M}–{instance.hora_fin:%H:%M}. "
        f"Bloques en conflicto: #{ids_conflicto}."
    )

    logger.warning(
        "Conflicto detectado — Docente %s | bloque nuevo: %s | solapados: %s",
        instance.docente,
        instance.pk,
        ids_conflicto,
    )

    # Alerta individual para el docente (dispara post_save → señal de notificaciones)
    Alerta.objects.create(
        tipo=Alerta.TipoAlerta.CONFLICTO,
        descripcion=descripcion_base,
        bloque_origen=instance,
        destinatario=instance.docente.user,
        formato_alerta=Alerta.FormatoAlerta.APP,
    )

    # Alertas masivas para gestores — bulk_create no dispara post_save,
    # por eso llamamos dispatch_alertas_bulk explícitamente.
    gestores = User.objects.filter(
        rol__in=[User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO],  # corregido: era ADMIN
        is_active=True,
    )
    gestores_list = list(gestores)
    if gestores_list:
        alertas_gestores = Alerta.objects.bulk_create([
            Alerta(
                tipo=Alerta.TipoAlerta.CONFLICTO,
                descripcion=descripcion_base,
                bloque_origen=instance,
                destinatario=gestor,
                formato_alerta=Alerta.FormatoAlerta.APP,
            )
            for gestor in gestores_list
        ])
        dispatch_alertas_bulk(alertas_gestores)