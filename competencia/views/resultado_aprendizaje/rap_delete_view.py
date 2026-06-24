from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import ProtectedError

from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView


class RAPDeleteView(CompetenciaBaseView):
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def delete(self, request, pk):
        rap, error = self.get_rap_or_404(pk)
        if error:
            return error

        try:
            rap.delete()
        except ProtectedError:
            return Response(
                {
                    'detail': (
                        f'No se puede eliminar el resultado "{rap.codigo}" '
                        f'porque tiene registros relacionados (por ejemplo, '
                        f'evaluaciones).'
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)