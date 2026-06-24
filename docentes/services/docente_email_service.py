# docentes/services/docente_email_service.py
from django.core.mail import send_mail
from django.conf import settings


def send_disponibilidad_change_email(
    admin_emails: list[str],
    docente_nombre: str,
    bloque_str: str,
    jornada: str,
    disponible: bool,
    motivo: str,
) -> None:
    """Notifica a los administradores el cambio de disponibilidad de un docente."""
    estado = 'Disponible' if disponible else 'No disponible'
    send_mail(
        subject=f'Cambio de disponibilidad — {docente_nombre} — Planify',
        message=(
            f'El docente {docente_nombre} ha cambiado su disponibilidad.\n\n'
            f'Bloque:       {bloque_str}\n'
            f'Jornada:      {jornada}\n'
            f'Nuevo estado: {estado}\n'
            f'Motivo:       {motivo or "Sin motivo especificado"}\n\n'
            f'Este cambio requiere revisión administrativa.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=admin_emails,
        fail_silently=False,
    )