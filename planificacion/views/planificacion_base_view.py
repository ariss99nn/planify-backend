# planificacion/views/planificacion_base_view.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from planificacion.models.bloque_competencia_model import BloqueCompetencia
from planificacion.models.item_plan_model import ItemPlan
from planificacion.models.plan_trimestral_model import PlanTrimestral


class PlanificacionBaseView(APIView):

    def get_plan_or_404(self, pk):
        obj = (
            PlanTrimestral.objects
            .select_related('ficha__version__programa', 'aprobado_por')
            .prefetch_related('items__competencia', 'items__docente__user')
            .filter(pk=pk)
            .first()
        )
        if obj is None:
            return None, Response(
                {'detail': 'Plan trimestral no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None

    def get_item_or_404(self, pk):
        obj = (
            ItemPlan.objects
            .select_related(
                'plan__ficha__version__programa',
                'competencia__asignatura',
                'docente__user',
            )
            .prefetch_related('bloques_ejecutados__bloque')
            .filter(pk=pk)
            .first()
        )
        if obj is None:
            return None, Response(
                {'detail': 'Ítem de plan no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None

    def get_bloque_competencia_or_404(self, pk):
        obj = (
            BloqueCompetencia.objects
            .select_related(
                'bloque__docente__user',
                'bloque__aula',
                'bloque__ficha',
                'item_plan__competencia',
                'item_plan__plan__ficha',
            )
            .filter(pk=pk)
            .first()
        )
        if obj is None:
            return None, Response(
                {'detail': 'Bloque de competencia no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None