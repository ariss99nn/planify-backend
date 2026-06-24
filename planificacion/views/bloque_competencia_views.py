# planificacion/views/bloque_competencia_views.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from planificacion.models.bloque_competencia_model import BloqueCompetencia
from planificacion.permissions import CanApprovePlan
from planificacion.serializers.bloque_competencia_serializer import (
    BloqueCompetenciaCreateSerializer,
    BloqueCompetenciaListSerializer,
)
from planificacion.views.planificacion_base_view import PlanificacionBaseView


class BloqueCompetenciaListView(PlanificacionBaseView):
    """
    GET /api/bloques-competencia/
    Filtros opcionales: ?plan=<id>  ?item=<id>
    """
    permission_classes = [IsAuthenticated, CanApprovePlan]

    def get(self, request):
        plan_id = request.query_params.get('plan')
        item_id = request.query_params.get('item')

        qs = BloqueCompetencia.objects.select_related(
            'bloque__docente__user',
            'bloque__aula',
            'item_plan__competencia',
            'item_plan__plan__ficha',
        )
        if plan_id:
            qs = qs.filter(item_plan__plan_id=plan_id)
        if item_id:
            qs = qs.filter(item_plan_id=item_id)

        return Response(BloqueCompetenciaListSerializer(qs, many=True).data)


class BloqueCompetenciaCreateView(PlanificacionBaseView):
    """POST /api/bloques-competencia/create/"""
    permission_classes = [IsAuthenticated, CanApprovePlan]

    def post(self, request):
        serializer = BloqueCompetenciaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bc = serializer.save()
        return Response(
            BloqueCompetenciaListSerializer(bc).data,
            status=status.HTTP_201_CREATED,
        )