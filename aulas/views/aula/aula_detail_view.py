from rest_framework.permissions import IsAuthenticated
from users.permissions import IsStaffLike
from rest_framework.response import Response
from aulas.serializers import AulaDetailSerializer
from aulas.views.aula_base_view import AulaBaseView

class AulaDetailView(AulaBaseView):
    permission_classes = [IsAuthenticated, IsStaffLike]

    def get(self, request, pk):
        aula, error = self.get_aula_or_404(pk)
        if error:
            return error
        return Response(AulaDetailSerializer(aula).data)