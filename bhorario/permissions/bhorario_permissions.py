# bhorario/permissions/bhorario_permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)
ROLES_VER     = (
    User.Rol.COORDINADOR,
    User.Rol.ADMINISTRATIVO,
    User.Rol.DOCENTE,
    User.Rol.ESTUDIANTE,
)


class CanManageHorario(BasePermission):
    """
    GET: gestión, docente (solo su horario) y estudiante (solo su ficha).
    POST / PUT / PATCH / DELETE: solo gestión.
    El filtrado granular por docente y por ficha de estudiante
    se hace en el queryset de cada vista.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.rol in ROLES_VER
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if request.user.rol in ROLES_GESTION:
            return True
        if request.method not in SAFE_METHODS:
            return False
        if request.user.rol == User.Rol.DOCENTE:
            return (
                hasattr(request.user, 'docente')
                and obj.docente == request.user.docente
            )
        if request.user.rol == User.Rol.ESTUDIANTE:
            return obj.ficha_id in (
                request.user.fichas_asignadas
                .filter(activo=True)
                .values_list('ficha_id', flat=True)
            )
        return False