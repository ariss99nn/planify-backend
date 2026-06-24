# docentes/views/docente_detail_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from docentes.permissions.docente_permissions import CanManageDocente
from docentes.serializers.docente_detail_serializer import DocenteDetailSerializer
from docentes.views.docente_base_view import DocenteBaseView


class DocenteDetailView(DocenteBaseView):
    permission_classes = [IsAuthenticated, CanManageDocente]

    def get(self, request, pk):
        docente, error = self.get_docente_or_404(pk)
        if error:
            return error

        self.check_object_permissions(request, docente)
        return Response(DocenteDetailSerializer(docente).data)