import logging
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_roles_and_permissions(sender, **kwargs):
    """
    Crea y sincroniza grupos y permisos después de cada migrate.
    Es idempotente: puede ejecutarse múltiples veces sin efectos secundarios.
    Se omite silenciosamente si los permisos custom aún no existen
    (primera migración antes de que el modelo User haya sido creado).
    """
    from users.models.user import User

    try:
        content_type = ContentType.objects.get_for_model(User)
    except Exception:
        return

    # ✅ Lista completa alineada con Meta.permissions del modelo User
    codenames = [
        # Visualización
        'ver_estudiantes',
        'ver_docentes',
        'ver_administrativos',
        'ver_coordinadores',
        # Horarios
        'ver_horarios',
        # CRUD
        'crear_usuarios',
        'editar_usuarios',
        'desactivar_usuarios',
        'eliminar_usuarios',
        # Roles y permisos
        'gestionar_permisos',
        'gestionar_roles',
    ]

    permisos = {}
    for codename in codenames:
        perm = Permission.objects.filter(
            codename=codename,
            content_type=content_type,
        ).first()

        if perm is None:
            logger.debug(
                "Permiso '%s' aún no existe. Se sincronizará en el próximo migrate.",
                codename,
            )
            return

        permisos[codename] = perm

    # Crear grupos si no existen
    coordinador, _  = Group.objects.get_or_create(name='COORDINADOR')
    administrativo, _ = Group.objects.get_or_create(name='ADMINISTRATIVO')
    docente, _      = Group.objects.get_or_create(name='DOCENTE')
    estudiante, _   = Group.objects.get_or_create(name='ESTUDIANTE')

    # ✅ Coordinador: todos los permisos
    coordinador.permissions.set(permisos.values())

    # ✅ Administrativo: todo excepto gestionar_roles y gestionar_permisos
    administrativo.permissions.set([
        permisos['ver_estudiantes'],
        permisos['ver_docentes'],
        permisos['ver_administrativos'],
        permisos['ver_coordinadores'],
        permisos['ver_horarios'],
        permisos['crear_usuarios'],
        permisos['editar_usuarios'],
        permisos['desactivar_usuarios'],
        permisos['eliminar_usuarios'],
    ])

    # ✅ Docente: ver estudiantes y horarios
    docente.permissions.set([
        permisos['ver_estudiantes'],
        permisos['ver_horarios'],
    ])

    # ✅ Estudiante: solo ver horarios
    estudiante.permissions.set([
        permisos['ver_horarios'],
    ])

    logger.info("Grupos y permisos sincronizados correctamente.")