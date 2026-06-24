from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from competencia.serializers import RAPCreateSerializer, RAPDetailSerializer
from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView


class RAPCreateView(CompetenciaBaseView):
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def post(self, request):
        serializer = RAPCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rap = serializer.save()
        return Response(
            RAPDetailSerializer(rap).data,
            status=status.HTTP_201_CREATED,
        )