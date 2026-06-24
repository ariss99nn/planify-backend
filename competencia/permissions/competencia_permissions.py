# competencia/permissions/competencia_permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)
ROLES_VER     = (
    User.Rol.COORDINADOR,
    User.Rol.ADMINISTRATIVO,
    User.Rol.DOCENTE,
    User.Rol.ESTUDIANTE,   # estudiantes ven RAPs de su carrera
)


class CanManageCompetencia(BasePermission):
    """
    GET: todo el staff + estudiantes (RAPs de su carrera).
    POST/PUT/PATCH/DELETE: solo gestión.
    Aplica a Asignatura, Competencia y ResultadoAprendizaje.
    El filtrado de qué RAPs ve cada estudiante se hace en el queryset.
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