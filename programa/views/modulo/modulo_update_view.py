# programa/views/modulo/modulo_update_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from programa.serializers import ModuloUpdateSerializer, ModuloDetailSerializer
from programa.permissions.programa_permissions import CanManagePrograma
from programa.views.programa_base_view import ProgramaBaseView


class ModuloUpdateView(ProgramaBaseView):
    permission_classes = [IsAuthenticated, CanManagePrograma]

    def patch(self, request, pk):
        modulo, error = self.get_modulo_or_404(pk)
        if error:
            return error
        serializer = ModuloUpdateSerializer(
            modulo, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ModuloDetailSerializer(modulo).data)