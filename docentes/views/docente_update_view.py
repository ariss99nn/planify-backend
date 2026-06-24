# docentes/views/docente_update_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from docentes.permissions.docente_permissions import CanManageDocente
from docentes.serializers.docente_update_serializer import DocenteUpdateSerializer
from docentes.serializers.docente_detail_serializer import DocenteDetailSerializer
from docentes.views.docente_base_view import DocenteBaseView

class DocenteUpdateView(DocenteBaseView):
    permission_classes = [IsAuthenticated, CanManageDocente]

    def patch(self, request, pk):
        docente, error = self.get_docente_or_404(pk)
        if error:
            return error

        self.check_object_permissions(request, docente)

        serializer = DocenteUpdateSerializer(
            docente,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(DocenteDetailSerializer(serializer.instance).data)