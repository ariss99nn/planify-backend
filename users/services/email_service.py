from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(email: str, code: str, expiry_minutes: int = 10) -> None:
    """Envía el código de verificación de correo al registrarse."""
    send_mail(
        subject='Verifica tu correo — Planify',
        message=(
            f'Tu código de verificación es: {code}\n'
            f'Expira en {expiry_minutes} minutos.\n\n'
            f'Si no creaste esta cuenta, ignora este mensaje.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def send_password_reset_email(email: str, code: str, expiry_minutes: int = None) -> None:
    """Envía el código de restablecimiento de contraseña."""
    if expiry_minutes is None:
        expiry_hours = getattr(settings, 'PASSWORD_RESET_EXPIRY_HOURS', 2)
        expiry_minutes = int(expiry_hours) * 60

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
    reset_url = f'{frontend_url}/#/reset-password/{code}'

    send_mail(
        subject='Restablecer contraseña — Planify',
        message=(
            f'Tu código de restablecimiento de contraseña es: {code}\n'
            f'Expira en {expiry_minutes // 60} hora(s).\n\n'
            f'Ve a este enlace para completar el restablecimiento sin copiar el código manualmente:\n'
            f'{reset_url}\n\n'
            f'Si no puedes abrir el enlace, copia el código en la app de Planify.\n'
            f'Si no solicitaste esto, ignora este mensaje.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def send_email_change_email(email: str, code: str, expiry_minutes: int = 10) -> None:
    """Envía el código de confirmación de cambio de correo."""
    send_mail(
        subject='Confirma tu nuevo correo — Planify',
        message=(
            f'Tu código de confirmación es: {code}\n'
            f'Expira en {expiry_minutes} minutos.\n\n'
            f'Si no solicitaste este cambio, contacta al administrador.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    
def send_welcome_email(email: str, nombre: str):
    subject = "Bienvenido a Planify"
    body = (
        f"Hola {nombre},\n\n"
        "Tu cuenta en Planify ha sido creada por un administrador.\n\n"
        "Puedes iniciar sesión con el correo y la contraseña que te asignaron.\n"
        "Si no reconoces este mensaje, ignóralo."
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])