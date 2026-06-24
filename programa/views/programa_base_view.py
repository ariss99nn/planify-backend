from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from programa.models.programa_model import Programa
from programa.models.version_programa_model import VersionPrograma
from programa.models.modulo_model import Modulo


class ProgramaBaseView(APIView):

    def get_programa_or_404(self, pk):
        obj = Programa.objects.prefetch_related(
            'versiones',
        ).filter(pk=pk).first()
        if obj is None:
            return None, Response(
                {'detail': 'Programa no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None

    def get_version_or_404(self, pk):
        obj = VersionPrograma.objects.select_related(
            'programa',
        ).prefetch_related(
            'modulos',
            'modulos__habilitaciones_docentes__docente__user',
        ).filter(pk=pk).first()
        if obj is None:
            return None, Response(
                {'detail': 'Versión no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None

    def get_modulo_or_404(self, pk):
        obj = Modulo.objects.select_related(
            'version__programa',
        ).prefetch_related(
            'habilitaciones_docentes__docente__user',
            'asignaturas',
        ).filter(pk=pk).first()
        if obj is None:
            return None, Response(
                {'detail': 'Módulo no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None