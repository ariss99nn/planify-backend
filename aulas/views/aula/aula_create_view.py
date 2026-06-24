from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from aulas.serializers import AulaCreateSerializer, AulaDetailSerializer
from aulas.permissions.aulas_permissions import CanManageAula
from aulas.views.aula_base_view import AulaBaseView

class AulaCreateView(AulaBaseView):
    permission_classes = [IsAuthenticated, CanManageAula]

    def post(self, request):
        serializer = AulaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        aula = serializer.save()
        return Response(
            AulaDetailSerializer(aula).data,
            status=status.HTTP_201_CREATED,
        )