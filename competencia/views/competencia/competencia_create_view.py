from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from competencia.serializers import CompetenciaCreateSerializer, CompetenciaDetailSerializer
from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView


class CompetenciaCreateView(CompetenciaBaseView):
    """Crea competencias PRINCIPALES (ligadas a una asignatura)."""
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def post(self, request):
        serializer = CompetenciaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comp = serializer.save()
        return Response(
            CompetenciaDetailSerializer(comp).data,
            status=status.HTTP_201_CREATED,
        )