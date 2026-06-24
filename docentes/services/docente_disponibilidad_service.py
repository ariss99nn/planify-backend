# docentes/services/docente_disponibilidad_service.py
from django.contrib.auth import get_user_model
from alertas.models.alerta_model import Alerta
from notificaciones.signals.notificaciones_signals import dispatch_alertas_bulk

User = get_user_model()


def _get_admin_users():
    return list(User.objects.filter(
        rol__in=[User.Rol.ADMINISTRATIVO, User.Rol.COORDINADOR],
        is_active=True,
    ))


def _get_admin_emails():
    return [u.email for u in _get_admin_users()]


def procesar_cambio_disponibilidad(instance, usuario) -> None:
    """
    Notifica a gestión cuando un docente marca una disponibilidad
    como no disponible. Ya no hay bloque asociado — se referencia
    por día y hora.
    """
    from docentes.services.docente_email_service import send_disponibilidad_change_email

    docente = instance.docente
    slot_str = (
        f"{instance.get_dia_semana_display()} "
        f"{instance.hora_inicio:%H:%M}–{instance.hora_fin:%H:%M}"
    )

    admin_emails = _get_admin_emails()
    if admin_emails:
        send_disponibilidad_change_email(
            admin_emails=admin_emails,
            docente_nombre=docente.nombre_completo,
            bloque_str=slot_str,
            jornada='—',
            disponible=False,
            motivo=instance.motivo,
        )

    # Alerta para cada gestor activo
    gestores = _get_admin_users()
    if gestores:
        descripcion = (
            f"El docente {docente.nombre_completo} registró no disponibilidad "
            f"el {slot_str}. Motivo: {instance.motivo or 'Sin especificar'}."
        )
        alertas = Alerta.objects.bulk_create([
            Alerta(
                tipo=Alerta.TipoAlerta.DISPONIBILIDAD,
                descripcion=descripcion,
                formato_alerta=Alerta.FormatoAlerta.APP,
                estado=Alerta.EstadoAlerta.PENDIENTE,
                destinatario=gestor,
            )
            for gestor in gestores
        ])
        dispatch_alertas_bulk(alertas)