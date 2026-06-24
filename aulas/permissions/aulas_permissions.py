from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)
ROLES_VER     = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO, User.Rol.DOCENTE)


class CanManageAula(BasePermission):
    """
    GET : COORDINADOR, ADMINISTRATIVO, DOCENTE.
    POST / PUT / PATCH / DELETE : COORDINADOR, ADMINISTRATIVO.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.rol in ROLES_VER
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.rol in ROLES_VER
        return request.user.rol in ROLES_GESTION


class CanManageBloque(BasePermission):
    """
    GET : COORDINADOR, ADMINISTRATIVO, DOCENTE.
    POST / PUT / PATCH / DELETE : COORDINADOR, ADMINISTRATIVO.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.rol in ROLES_VER
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.rol in ROLES_VER
        return request.user.rol in ROLES_GESTION


class CanManageEquipamiento(BasePermission):
    """
    GET : COORDINADOR, ADMINISTRATIVO, DOCENTE.
    POST / PUT / PATCH / DELETE : COORDINADOR, ADMINISTRATIVO.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.rol in ROLES_VER
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.rol in ROLES_VER
        return request.user.rol in ROLES_GESTION


class CanChangeAulaEstado(BasePermission):
    """
    CORRECCIÓN: permiso específico para el endpoint PATCH /aulas/{pk}/estado/.
    DOCENTE puede reportar/cambiar el estado de un aula (p.ej. mantenimiento).
    COORDINADOR y ADMINISTRATIVO también tienen acceso total.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.rol in ROLES_VER
        # Escritura permitida a los tres roles
        return request.user.rol in ROLES_VER

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.rol in ROLES_VER
        return request.user.rol in ROLES_VER