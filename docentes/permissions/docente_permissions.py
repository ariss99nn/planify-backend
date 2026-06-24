# docentes/permissions/docente_permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)


class CanManageDocente(BasePermission):
    """
    GET: gestión y el propio docente (solo su perfil).
    POST/PUT/PATCH/DELETE: solo gestión.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.rol in (*ROLES_GESTION, User.Rol.DOCENTE)
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if request.user.rol in ROLES_GESTION:
                return True
            return (
                request.user.rol == User.Rol.DOCENTE
                and hasattr(request.user, 'docente')
                and request.user.docente == obj
            )
        return request.user.rol in ROLES_GESTION


class CanManageHabilitacion(BasePermission):
    """
    GET: gestión y el propio docente (solo sus habilitaciones).
    POST/PUT/PATCH/DELETE: solo gestión.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.rol in (*ROLES_GESTION, User.Rol.DOCENTE)
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if request.user.rol in ROLES_GESTION:
                return True
            return (
                request.user.rol == User.Rol.DOCENTE
                and hasattr(request.user, 'docente')
                and obj.docente == request.user.docente
            )
        return request.user.rol in ROLES_GESTION


class CanManageDisponibilidad(BasePermission):
    """
    GET: gestión y el propio docente.
    POST/PATCH: gestión y el propio docente (solo la suya).
    DELETE: solo gestión.
    Validación de disponibilidad (campo validada): solo gestión,
    controlado en el serializer con read_only condicional.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in (*ROLES_GESTION, User.Rol.DOCENTE)

    def has_object_permission(self, request, view, obj):
        if request.user.rol in ROLES_GESTION:
            return True
        if request.user.rol != User.Rol.DOCENTE:
            return False
        es_suya = (
            hasattr(request.user, 'docente')
            and obj.docente == request.user.docente
        )
        if not es_suya:
            return False
        # Docente no puede eliminar sus propias disponibilidades
        # (requiere gestión para mantener trazabilidad)
        if request.method == 'DELETE':
            return False
        return True