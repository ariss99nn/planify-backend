# users/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)


class HasRole(BasePermission):
    allowed_roles: tuple = ()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in self.allowed_roles


class IsEstudiante(HasRole):
    allowed_roles = (User.Rol.ESTUDIANTE,)


class IsDocente(HasRole):
    allowed_roles = (User.Rol.DOCENTE,)


class IsCoordinador(HasRole):
    allowed_roles = (User.Rol.COORDINADOR,)


class IsAdministrativo(HasRole):
    allowed_roles = (User.Rol.ADMINISTRATIVO,)


class IsManager(HasRole):
    allowed_roles = ROLES_GESTION


class IsManagerOrDocente(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in ROLES_GESTION or request.user.rol == User.Rol.DOCENTE


class IsStaffLike(HasRole):
    allowed_roles = (
        User.Rol.DOCENTE,
        User.Rol.COORDINADOR,
        User.Rol.ADMINISTRATIVO,
    )


class CanManageUser(BasePermission):
    """
    CRUD de usuarios: solo gestión.
    Nadie puede gestionarse a sí mismo por esta vía.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if obj == request.user:
            return False
        return request.user.rol in ROLES_GESTION


class CanDeactivateOrRestoreCoordinator(BasePermission):
    """
    Desactivar o restaurar una cuenta de COORDINADOR:
    solo otro COORDINADOR puede hacerlo.
    Para objetos que NO son coordinador, devuelve True
    y deja que CanManageUser resuelva.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if obj.rol != User.Rol.COORDINADOR:
            return True
        return request.user.rol == User.Rol.COORDINADOR