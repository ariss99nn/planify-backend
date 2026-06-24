import logging
from django.db import transaction
from users.models.email_verification import EmailVerification

logger = logging.getLogger(__name__)


def verify_email_code(user, code: str):
    """
    Verifica un código de email fuera de contexto HTTP.
    Usar en: tareas Celery, comandos de gestión, tests.
    Para vistas DRF usar EmailVerificationSerializer directamente
    (el serializer delega la lógica de activación en _activate_user).

    Retorna: (True, mensaje) o (False, mensaje)
    """
    try:
        verification = EmailVerification.objects.filter(
            user=user,
            is_used=False,
        ).latest('created_at')
    except EmailVerification.DoesNotExist:
        return False, "Código inválido."

    if not verification.is_valid():                        # ✅ usa is_valid() del modelo
        return False, "El código ha expirado."

    if verification.code.strip() != str(code).strip():
        return False, "Código incorrecto."

    with transaction.atomic():
        verification.mark_as_verified()                    # ✅ usa método del modelo
        _activate_user(user)

    return True, "Email verificado correctamente."


def _activate_user(user) -> None:
    """
    Activa un usuario tras verificación exitosa de email.
    Función interna — usada tanto por verify_email_code como por
    EmailVerificationSerializer para garantizar consistencia.
    """
    user.is_active = True
    user.email_verificado = True                           # ✅ nuevo campo del modelo
    user.save(update_fields=['is_active', 'email_verificado'])
    logger.info("Usuario activado tras verificación de email: %s", user.email)