# analitica/permissions/analitica_permissions.py
# (contenido que estaba en __init__.py — movido a su propio archivo)
from rest_framework.permissions import BasePermission
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)


class CanViewAnalitica(BasePermission):
    """
    Solo COORDINADOR y ADMINISTRATIVO acceden al dashboard
    de analítica y snapshots históricos.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        return request.user.rol in ROLES_GESTION