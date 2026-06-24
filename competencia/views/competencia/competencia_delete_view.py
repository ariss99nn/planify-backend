from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import ProtectedError

from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView


class CompetenciaDeleteView(CompetenciaBaseView):
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def delete(self, request, pk):
        competencia, error = self.get_competencia_or_404(pk)
        if error:
            return error

        total_resultados = competencia.resultados.count()
        if total_resultados:
            return Response(
                {
                    'detail': (
                        f'No se puede eliminar la competencia "{competencia.codigo}": '
                        f'tiene {total_resultados} resultado(s) de aprendizaje '
                        f'asociado(s). Elimínalos primero.'
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        if competencia.es_induccion:
            return Response(
                {
                    'detail': (
                        'No se puede eliminar una competencia marcada como '
                        'inducción. Quita la marca de inducción antes de '
                        'eliminarla.'
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        try:
            competencia.delete()
        except ProtectedError:
            return Response(
                {
                    'detail': (
                        f'No se puede eliminar la competencia "{competencia.codigo}" '
                        f'porque tiene registros relacionados.'
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)