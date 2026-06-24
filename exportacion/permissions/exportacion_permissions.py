# exportacion/permissions/exportacion_permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)


class CanExport(BasePermission):
    """
    Solo COORDINADOR y ADMINISTRATIVO pueden ejecutar exportaciones
    y ver el log de RegistroExportacion.
    Docentes y estudiantes no tienen acceso a este módulo.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        return request.user.rol in ROLES_GESTION


class CanViewRegistroExportacion(BasePermission):
    """
    GET: ambos roles de gestión ven todos los registros.
    El COORDINADOR ve todos sin restricción.
    El ADMINISTRATIVO ve todos — si en el futuro
    se quiere restringir a 'solo los suyos', se cambia
    has_object_permission sin tocar has_permission.
    POST/PUT/PATCH/DELETE: bloqueado — los registros
    son inmutables, se crean solo desde el proceso de exportación.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method not in SAFE_METHODS:
            return False
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return False
        return request.user.rol in ROLES_GESTION