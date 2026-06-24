# docentes/views/docente_habilitacion_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from docentes.models.docente_habilitacion_model import HabilitacionDocente
from docentes.serializers.docente_habilitacion_serializer import (
    HabilitacionDocenteListSerializer,
    HabilitacionDocenteCreateSerializer,
    HabilitacionDocenteUpdateSerializer,
)
from docentes.permissions.docente_permissions import CanManageHabilitacion
from docentes.filters.docente_pagination import DocentePagination
from docentes.views.docente_base_view import DocenteBaseView
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)

class HabilitacionDocenteListCreateView(DocenteBaseView):
    """
    GET  /api/habilitaciones/  → gestión ve todas; docente solo las suyas.
    POST /api/habilitaciones/  → solo gestión.
    """
    permission_classes = [IsAuthenticated, CanManageHabilitacion]

    def _base_queryset(self):
        return HabilitacionDocente.objects.select_related(
            'docente__user',
            'modulo__version__programa',
            'asignatura__modulo',
        )

    def get(self, request):
        user = request.user
        qs = self._base_queryset()

        if user.rol not in ROLES_GESTION:
            qs = qs.filter(docente=user.docente) if hasattr(user, 'docente') else qs.none()

        # Filtros opcionales
        activo     = request.query_params.get('activo')
        nivel      = request.query_params.get('nivel')
        docente_id = request.query_params.get('docente')

        if activo is not None:
            qs = qs.filter(activo=activo.lower() == 'true')
        if nivel:
            qs = qs.filter(nivel=nivel)
        if docente_id and user.rol in ROLES_GESTION:
            qs = qs.filter(docente_id=docente_id)

        paginator = DocentePagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(
            HabilitacionDocenteListSerializer(page, many=True).data
        )

    def post(self, request):
        serializer = HabilitacionDocenteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hab = serializer.save()
        return Response(
            HabilitacionDocenteListSerializer(hab).data,
            status=status.HTTP_201_CREATED,
        )


class HabilitacionDocenteDetailView(DocenteBaseView):
    """
    PATCH /api/habilitaciones/{pk}/  → solo gestión.
    """
    permission_classes = [IsAuthenticated, CanManageHabilitacion]

    def _get_habilitacion(self, pk):
        return (
            HabilitacionDocente.objects
            .select_related('docente__user', 'modulo', 'asignatura')
            .filter(pk=pk)
            .first()
        )

    def patch(self, request, pk):
        hab = self._get_habilitacion(pk)
        if hab is None:
            return Response(
                {'detail': 'Habilitación no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, hab)

        serializer = HabilitacionDocenteUpdateSerializer(
            hab, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        hab = serializer.save()
        return Response(HabilitacionDocenteListSerializer(hab).data)