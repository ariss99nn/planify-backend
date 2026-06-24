from rest_framework.permissions import IsAuthenticated
from users.permissions import IsStaffLike
from rest_framework.response import Response
from aulas.serializers import EquipamientoDetailSerializer
from aulas.views.aula_base_view import AulaBaseView

class EquipamientoDetailView(AulaBaseView):
    permission_classes = [IsAuthenticated, IsStaffLike]

    def get(self, request, pk):
        equip, error = self.get_equipamiento_or_404(pk)
        if error:
            return error
        return Response(EquipamientoDetailSerializer(equip).data)