from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import ProtectedError

from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView


class AsignaturaDeleteView(CompetenciaBaseView):
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def delete(self, request, pk):
        asignatura, error = self.get_asignatura_or_404(pk)
        if error:
            return error

        total_competencias = asignatura.competencias.count()
        if total_competencias:
            return Response(
                {
                    'detail': (
                        f'No se puede eliminar la asignatura "{asignatura.nombre}": '
                        f'tiene {total_competencias} competencia(s) asociada(s). '
                        f'Elimínalas o reasígnalas a otra asignatura primero.'
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        try:
            asignatura.delete()
        except ProtectedError:
            return Response(
                {
                    'detail': (
                        f'No se puede eliminar la asignatura "{asignatura.nombre}" '
                        f'porque tiene registros relacionados (por ejemplo, '
                        f'habilitaciones de docentes).'
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)