# CORRECCIÓN: renombrado de base_view.py → aula_base_view.py
# para coincidir con todos los imports: from back.aulas.views.aula_base_view import AulaBaseView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from aulas.models.aula_model import Aula
from aulas.models.bloque_model import Bloque
from aulas.models.equipamiento_model import Equipamiento


class AulaBaseView(APIView):

    def get_aula_or_404(self, pk):
        aula = (
            Aula.objects
            .select_related('bloque')
            .prefetch_related('equipamiento')
            .filter(pk=pk)
            .first()
        )
        if aula is None:
            return None, Response(
                {'detail': 'Aula no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return aula, None

    def get_bloque_or_404(self, pk):
        bloque = Bloque.objects.filter(pk=pk).first()
        if bloque is None:
            return None, Response(
                {'detail': 'Bloque no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return bloque, None

    def get_equipamiento_or_404(self, pk):
        equip = Equipamiento.objects.filter(pk=pk).first()
        if equip is None:
            return None, Response(
                {'detail': 'Equipamiento no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return equip, None