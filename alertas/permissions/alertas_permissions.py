# alertas/permissions/alertas_permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)


class CanManageAlerta(BasePermission):
    """
    GET: gestión (todas) y docente/estudiante (solo las suyas).
    POST/PUT/PATCH/DELETE: solo gestión.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.rol in (
                *ROLES_GESTION,
                User.Rol.DOCENTE,
                User.Rol.ESTUDIANTE,
            )
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if request.user.rol in ROLES_GESTION:
            return True
        if request.method in SAFE_METHODS:
            return obj.destinatario == request.user
        return False