from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from aulas.serializers import BloqueCreateSerializer, BloqueDetailSerializer
from aulas.permissions.aulas_permissions import CanManageBloque
from aulas.views.aula_base_view import AulaBaseView

class BloqueCreateView(AulaBaseView):
    permission_classes = [IsAuthenticated, CanManageBloque]

    def post(self, request):
        serializer = BloqueCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bloque = serializer.save()
        return Response(
            BloqueDetailSerializer(bloque).data,
            status=status.HTTP_201_CREATED,
        )