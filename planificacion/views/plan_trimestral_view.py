# planificacion/views/plan_trimestral_views.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from planificacion.filters.planificacion_filters import PlanTrimestralFilter
from planificacion.filters.planificacion_pagination import PlanificacionPagination
from planificacion.models.plan_trimestral_model import PlanTrimestral
from planificacion.permissions import CanApprovePlan, CanManagePlan
from planificacion.serializers.plan_trimestral.plan_trimestral_aprobar_serializer import (
    PlanTrimestralCambiarEstadoSerializer,
)
from planificacion.serializers.plan_trimestral.plan_trimestral_create_serializer import (
    PlanTrimestralCreateSerializer,
)
from planificacion.serializers.plan_trimestral.plan_trimestral_detail_serializer import (
    PlanTrimestralDetailSerializer,
)
from planificacion.serializers.plan_trimestral.plan_trimestral_list_serializer import (
    PlanTrimestralListSerializer,
)
from planificacion.serializers.plan_trimestral.plan_trimestral_update_serializer import (
    PlanTrimestralUpdateSerializer,
)
from planificacion.services.horario_generator_service import HorarioGeneratorService
from planificacion.views.planificacion_base_view import PlanificacionBaseView
from users.models.user import User


class PlanTrimestralListView(PlanificacionBaseView):
    """
    GET /api/planes/
    COORDINADOR / ADMINISTRATIVO → todos los planes.
    DOCENTE → solo planes donde tiene ítems asignados.
    """
    permission_classes = [IsAuthenticated, CanManagePlan]

    def _get_queryset(self, request):
        user = request.user
        qs = PlanTrimestral.objects.select_related(
            'ficha__version__programa', 'aprobado_por'
        )
        if user.rol in {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO}:
            return qs
        if user.rol == User.Rol.DOCENTE:
            if not hasattr(user, 'docente'):
                return qs.none()
            return qs.filter(items__docente=user.docente).distinct()
        return qs.none()

    def get(self, request):
        queryset  = self._get_queryset(request)
        filterset = PlanTrimestralFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        paginator = PlanificacionPagination()
        page      = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            PlanTrimestralListSerializer(page, many=True).data
        )


class PlanTrimestralDetailView(PlanificacionBaseView):
    """
    GET /api/planes/{id}/
    Gestión ve cualquier plan; docente solo los suyos (chequeado por CanManagePlan).
    """
    permission_classes = [IsAuthenticated, CanManagePlan]

    def get(self, request, pk):
        plan, error = self.get_plan_or_404(pk)
        if error:
            return error
        self.check_object_permissions(request, plan)
        return Response(PlanTrimestralDetailSerializer(plan).data)


class PlanTrimestralCreateView(PlanificacionBaseView):
    """POST /api/planes/create/"""
    permission_classes = [IsAuthenticated, CanManagePlan]

    def post(self, request):
        serializer = PlanTrimestralCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.save()
        return Response(
            PlanTrimestralDetailSerializer(plan).data,
            status=status.HTTP_201_CREATED,
        )


class PlanTrimestralUpdateView(PlanificacionBaseView):
    """PATCH /api/planes/{id}/update/"""
    permission_classes = [IsAuthenticated, CanManagePlan]

    # Estados que bloquean cualquier edición de fechas
    _ESTADOS_BLOQUEADOS = {
        PlanTrimestral.EstadoPlan.APROBADO,
        PlanTrimestral.EstadoPlan.EN_EJECUCION,
        PlanTrimestral.EstadoPlan.CERRADO,
    }

    def patch(self, request, pk):
        plan, error = self.get_plan_or_404(pk)
        if error:
            return error
        self.check_object_permissions(request, plan)

        if plan.estado in self._ESTADOS_BLOQUEADOS:
            return Response(
                {'detail': 'No se puede editar un plan en este estado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PlanTrimestralUpdateSerializer(
            plan, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        plan.refresh_from_db()
        return Response(PlanTrimestralDetailSerializer(plan).data)


class PlanTrimestralCambiarEstadoView(PlanificacionBaseView):
    """
    PATCH /api/planes/{id}/estado/
    Gestiona cualquier transición de estado según el flujo definido.
    Exclusivo para COORDINADOR y ADMINISTRATIVO.
    """
    permission_classes = [IsAuthenticated, CanApprovePlan]

    def patch(self, request, pk):
        plan, error = self.get_plan_or_404(pk)
        if error:
            return error
        serializer = PlanTrimestralCambiarEstadoSerializer(
            plan,
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        plan.refresh_from_db()
        return Response(PlanTrimestralDetailSerializer(plan).data)


class GenerarHorarioView(PlanificacionBaseView):
    """
    POST /api/planes/{id}/generar-horario/
    Genera bloques horarios automáticamente desde el plan aprobado.
    Exclusivo para COORDINADOR y ADMINISTRATIVO.
    """
    permission_classes = [IsAuthenticated, CanApprovePlan]

    def post(self, request, pk):
        plan, error = self.get_plan_or_404(pk)
        if error:
            return error

        if plan.estado != PlanTrimestral.EstadoPlan.APROBADO:
            return Response(
                {'detail': 'El plan debe estar en estado APROBADO para generar horarios.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            resultado = HorarioGeneratorService(plan).generar()
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(resultado, status=status.HTTP_201_CREATED)