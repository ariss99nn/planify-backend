import logging
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)


def sync_user_group(user) -> None:
    """
    Sincroniza el usuario al grupo de Django que corresponde a su rol.
    Requiere que los grupos existan en la DB (creados por la signal post_migrate).
    Llamar en: creación de usuario y cambio de rol.

    Lanza RuntimeError en entornos de desarrollo si el grupo no existe,
    para detectar migraciones faltantes temprano.
    En producción loggea el error sin interrumpir el flujo.
    """
    from django.conf import settings

    try:
        group = Group.objects.get(name=user.rol)
    except Group.DoesNotExist:
        msg = (
            f"Grupo '{user.rol}' no existe en la DB. "
            f"Ejecuta las migraciones o el comando de sincronización de grupos."
        )
        logger.error(msg)

        # ✅ En desarrollo lo hacemos visible; en producción no interrumpimos
        if settings.DEBUG:
            raise RuntimeError(msg)
        return

    user.groups.set([group])
    logger.debug("Usuario '%s' sincronizado al grupo '%s'.", user.email, user.rol)