from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from competencia.models.competencia_model import Competencia
from competencia.serializers import (
    CompetenciaUpdateSerializer,
    CompetenciaTransversalUpdateSerializer,
    CompetenciaDetailSerializer,
)
from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView


class CompetenciaUpdateView(CompetenciaBaseView):
    """
    PATCH único para competencias PRINCIPALES y TRANSVERSALES.
    El serializer aplicado depende del tipo de la competencia existente.
    """
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def patch(self, request, pk):
        competencia, error = self.get_competencia_or_404(pk)
        if error:
            return error

        if competencia.tipo == Competencia.TipoCompetencia.TRANSVERSAL:
            serializer_class = CompetenciaTransversalUpdateSerializer
        else:
            serializer_class = CompetenciaUpdateSerializer

        serializer = serializer_class(competencia, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CompetenciaDetailSerializer(competencia).data)