# ficha/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)


class CanManageFicha(BasePermission):
    """
    GET: gestión y docente (solo fichas donde es jefe_grupo).
    POST/PUT/PATCH/DELETE: solo gestión.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.rol in (*ROLES_GESTION, User.Rol.DOCENTE)
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if request.user.rol in ROLES_GESTION:
            return True
        if request.user.rol == User.Rol.DOCENTE:
            return (
                obj.jefe_grupo is not None
                and obj.jefe_grupo.user_id == request.user.pk
            )
        return False


class CanManageEstudiante(BasePermission):
    """
    GET: gestión y docente (solo estudiantes de su ficha).
    POST/PUT/PATCH/DELETE: solo gestión.
    El filtrado de qué estudiantes ve el docente se hace en el queryset.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.rol in (*ROLES_GESTION, User.Rol.DOCENTE)
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        if request.user.rol in ROLES_GESTION:
            return True
        if request.user.rol == User.Rol.DOCENTE:
            # Docente ve estudiantes de fichas donde es jefe_grupo
            return (
                hasattr(request.user, 'docente')
                and obj.ficha.jefe_grupo == request.user.docente
            )
        return False


class CanViewPropioPerfil(BasePermission):
    """
    Un estudiante puede ver su propia FichaEstudiante
    (su estado, etapa, ficha asignada).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in (
            *ROLES_GESTION,
            User.Rol.DOCENTE,
            User.Rol.ESTUDIANTE,
        )

    def has_object_permission(self, request, view, obj):
        if request.user.rol in (*ROLES_GESTION, User.Rol.DOCENTE):
            return True
        # Estudiante solo ve su propio registro
        return obj.estudiante == request.user