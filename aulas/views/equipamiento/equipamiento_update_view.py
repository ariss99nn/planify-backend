from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from aulas.serializers import EquipamientoUpdateSerializer, EquipamientoDetailSerializer
from aulas.permissions.aulas_permissions import CanManageEquipamiento
from aulas.views.aula_base_view import AulaBaseView

class EquipamientoUpdateView(AulaBaseView):
    permission_classes = [IsAuthenticated, CanManageEquipamiento]

    def patch(self, request, pk):
        equip, error = self.get_equipamiento_or_404(pk)
        if error:
            return error
        serializer = EquipamientoUpdateSerializer(equip, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(EquipamientoDetailSerializer(serializer.instance).data)