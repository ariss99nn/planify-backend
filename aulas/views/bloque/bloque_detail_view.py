from rest_framework.permissions import IsAuthenticated
from users.permissions import IsStaffLike
from rest_framework.response import Response
from aulas.serializers import BloqueDetailSerializer
from aulas.views.aula_base_view import AulaBaseView

class BloqueDetailView(AulaBaseView):
    permission_classes = [IsAuthenticated, IsStaffLike]

    def get(self, request, pk):
        bloque, error = self.get_bloque_or_404(pk)
        if error:
            return error
        return Response(BloqueDetailSerializer(bloque).data)