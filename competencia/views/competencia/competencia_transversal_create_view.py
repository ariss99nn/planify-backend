from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from competencia.serializers import CompetenciaTransversalCreateSerializer, CompetenciaDetailSerializer
from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView


class CompetenciaTransversalCreateView(CompetenciaBaseView):
    """Crea competencias TRANSVERSALES (pertenecen al centro)."""
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def post(self, request):
        serializer = CompetenciaTransversalCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comp = serializer.save()
        return Response(
            CompetenciaDetailSerializer(comp).data,
            status=status.HTTP_201_CREATED,
        )