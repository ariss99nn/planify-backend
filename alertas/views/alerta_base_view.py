# alertas/views/alerta_base_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from alertas.models.alerta_model import Alerta


class AlertaBaseView(APIView):

    def get_alerta_or_404(self, pk):
        obj = Alerta.objects.select_related(
            'bloque_origen', 'destinatario'
        ).filter(pk=pk).first()
        if obj is None:
            return None, Response(
                {'detail': 'Alerta no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return obj, None