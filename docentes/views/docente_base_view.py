# docentes/views/docente_base_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from docentes.models.docente_model import Docente

class DocenteBaseView(APIView):

    def get_docente_or_404(self, pk):
        docente = Docente.objects.select_related('user').filter(pk=pk).first()
        if docente is None:
            return None, Response(
                {'detail': 'Docente no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return docente, None