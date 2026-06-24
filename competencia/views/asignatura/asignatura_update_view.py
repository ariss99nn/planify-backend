from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from competencia.serializers import AsignaturaUpdateSerializer, AsignaturaDetailSerializer
from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView


class AsignaturaUpdateView(CompetenciaBaseView):
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def patch(self, request, pk):
        asignatura, error = self.get_asignatura_or_404(pk)
        if error:
            return error
        serializer = AsignaturaUpdateSerializer(
            asignatura, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AsignaturaDetailSerializer(asignatura).data)