from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from competencia.serializers import AsignaturaCreateSerializer, AsignaturaDetailSerializer
from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView


class AsignaturaCreateView(CompetenciaBaseView):
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def post(self, request):
        serializer = AsignaturaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asignatura = serializer.save()
        return Response(
            AsignaturaDetailSerializer(asignatura).data,
            status=status.HTTP_201_CREATED,
        )