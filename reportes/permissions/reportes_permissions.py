# reportes/permissions/reportes_permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models.user import User

ROLES_GESTION   = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)
TIPOS_DOCENTE   = {'FICHAS', 'HORARIOS'}


class CanManageReporte(BasePermission):
    """
    GET: gestión (todos) y docente (solo los suyos).
    POST: gestión (cualquier tipo) y docente (solo FICHAS y HORARIOS).
    DELETE: solo gestión.
    La validación del tipo permitido para docentes se hace
    en el serializer (validate_tipo).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.rol in (*ROLES_GESTION, User.Rol.DOCENTE)
        if request.method == 'POST':
            return request.user.rol in (*ROLES_GESTION, User.Rol.DOCENTE)
        # PUT/PATCH/DELETE
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if request.user.rol in ROLES_GESTION:
            return True
        if request.user.rol == User.Rol.DOCENTE:
            if request.method not in SAFE_METHODS:
                return False
            return obj.usuario == request.user
        return False


class CanExport(BasePermission):
    """
    Solo COORDINADOR y ADMINISTRATIVO pueden exportar datos
    y ver el log de exportaciones.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        return request.user.rol in ROLES_GESTION
    
    

class CanManageNovedad(BasePermission):
    """
    Solo COORDINADOR y ADMINISTRATIVO acceden a novedades.
    Los docentes no tienen acceso a este módulo.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        return request.user.rol in ROLES_GESTION