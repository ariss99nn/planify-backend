from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from aulas.serializers import AulaEstadoSerializer, AulaDetailSerializer
from aulas.permissions.aulas_permissions import CanChangeAulaEstado
from aulas.views.aula_base_view import AulaBaseView

class AulaEstadoView(AulaBaseView):
    permission_classes = [IsAuthenticated, CanChangeAulaEstado]

    def patch(self, request, pk):
        aula, error = self.get_aula_or_404(pk)
        if error:
            return error
        serializer = AulaEstadoSerializer(aula, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AulaDetailSerializer(serializer.instance).data)