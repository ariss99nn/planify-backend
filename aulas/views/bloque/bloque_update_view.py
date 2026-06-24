from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from aulas.serializers import BloqueUpdateSerializer, BloqueDetailSerializer
from aulas.permissions.aulas_permissions import CanManageBloque
from aulas.views.aula_base_view import AulaBaseView

class BloqueUpdateView(AulaBaseView):
    permission_classes = [IsAuthenticated, CanManageBloque]

    def patch(self, request, pk):
        bloque, error = self.get_bloque_or_404(pk)
        if error:
            return error
        serializer = BloqueUpdateSerializer(bloque, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(BloqueDetailSerializer(serializer.instance).data)