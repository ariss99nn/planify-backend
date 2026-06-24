from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from competencia.models.asignatura_model import Asignatura
from competencia.models.competencia_model import Competencia
from competencia.models.resultado_aprendizaje_model import ResultadoAprendizaje


class CompetenciaBaseView(APIView):

    def get_asignatura_or_404(self, pk):
        obj = Asignatura.objects.select_related(
            'modulo__version__programa',
        ).prefetch_related(
            'competencias__resultados',
            'habilitaciones_docentes__docente__user',
        ).filter(pk=pk).first()
        if obj is None:
            return None, Response(
                {'detail': 'Asignatura no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None

    def get_competencia_or_404(self, pk):
        obj = Competencia.objects.select_related(
            'asignatura__modulo__version__programa',
        ).prefetch_related(
            'resultados',
        ).filter(pk=pk).first()
        if obj is None:
            return None, Response(
                {'detail': 'Competencia no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None

    def get_rap_or_404(self, pk):
        obj = ResultadoAprendizaje.objects.select_related(
            'competencia__asignatura__modulo',
        ).filter(pk=pk).first()
        if obj is None:
            return None, Response(
                {'detail': 'Resultado de aprendizaje no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None