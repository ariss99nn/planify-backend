# docentes/views/docente_deactivate_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from docentes.permissions.docente_permissions import CanManageDocente
from docentes.serializers.docente_deactivate_serializer import DocenteDeactivateSerializer
from docentes.views.docente_base_view import DocenteBaseView

class DocenteDeactivateView(DocenteBaseView):
    permission_classes = [IsAuthenticated, CanManageDocente]

    def patch(self, request, pk):
        docente, error = self.get_docente_or_404(pk)
        if error:
            return error

        self.check_object_permissions(request, docente)

        serializer = DocenteDeactivateSerializer(docente, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Perfil docente desactivado correctamente.'})