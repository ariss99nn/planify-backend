from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from aulas.serializers import EquipamientoCreateSerializer, EquipamientoDetailSerializer
from aulas.permissions.aulas_permissions import CanManageEquipamiento
from aulas.views.aula_base_view import AulaBaseView

class EquipamientoCreateView(AulaBaseView):
    permission_classes = [IsAuthenticated, CanManageEquipamiento]

    def post(self, request):
        serializer = EquipamientoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        equip = serializer.save()
        return Response(
            EquipamientoDetailSerializer(equip).data,
            status=status.HTTP_201_CREATED,
        )