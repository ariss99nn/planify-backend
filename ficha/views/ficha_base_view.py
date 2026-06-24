# ficha/views/ficha_base_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ficha.models.ficha_model import Ficha
from ficha.models.ficha_estudiante_model import FichaEstudiante


class FichaBaseView(APIView):

    def get_ficha_or_404(self, pk, prefetch=None):
        """
        Retorna (ficha, None) o (None, Response 404).
        prefetch: lista de strings para prefetch_related opcional,
                  p.ej. ['historial_etapas'] en el detail endpoint.
        """
        qs = Ficha.objects.select_related('version__programa', 'jefe_grupo')
        if prefetch:
            qs = qs.prefetch_related(*prefetch)
        obj = qs.filter(pk=pk).first()
        if obj is None:
            return None, Response(
                {'detail': 'Ficha no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None

    def get_ficha_estudiante_or_404(self, ficha, estudiante_pk):
        obj = FichaEstudiante.objects.select_related(
            'estudiante', 'ficha'
        ).filter(ficha=ficha, pk=estudiante_pk).first()
        if obj is None:
            return None, Response(
                {'detail': 'Estudiante no encontrado en esta ficha.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None

    def es_jefe_de_ficha(self, user, ficha):
        return (
            ficha.jefe_grupo is not None
            and ficha.jefe_grupo.user_id == user.pk
        )