# planificacion/permissions.py
from rest_framework.permissions import SAFE_METHODS, BasePermission

from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)


class CanManagePlan(BasePermission):
    """
    Lectura  → gestión + docente (solo planes/ítems propios, filtrado en queryset).
    Escritura → solo gestión.
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
            # obj puede ser PlanTrimestral o ItemPlan
            plan = obj if hasattr(obj, 'items') else getattr(obj, 'plan', None)
            if plan is None or not hasattr(request.user, 'docente'):
                return False
            return plan.items.filter(docente=request.user.docente).exists()
        return False


class CanApprovePlan(BasePermission):
    """
    Transiciones de estado y generación de horarios.
    Exclusivo para COORDINADOR y ADMINISTRATIVO.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in ROLES_GESTION

    def has_object_permission(self, request, view, obj):
        return request.user.rol in ROLES_GESTION