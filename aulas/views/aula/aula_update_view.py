from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from aulas.serializers import AulaUpdateSerializer, AulaDetailSerializer
from aulas.permissions.aulas_permissions import CanManageAula
from aulas.views.aula_base_view import AulaBaseView

class AulaUpdateView(AulaBaseView):
    permission_classes = [IsAuthenticated, CanManageAula]

    def patch(self, request, pk):
        aula, error = self.get_aula_or_404(pk)
        if error:
            return error
        serializer = AulaUpdateSerializer(aula, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AulaDetailSerializer(serializer.instance).data)