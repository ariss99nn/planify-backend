# bhorario/views/bloque_update_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bhorario.views.bhorario_base import BhorarioBaseView
from bhorario.permissions.bhorario_permissions import CanManageHorario
from bhorario.serializers import BloqueHorarioUpdateSerializer, BloqueHorarioDetailSerializer
from bhorario.services.bloque_service import BloqueHorarioService, ColisionError
from bhorario.models.bloque_horario_model import BloqueHorario


class BloqueHorarioUpdateView(BhorarioBaseView):
    permission_classes = [IsAuthenticated, CanManageHorario]

    def patch(self, request, pk):
        bloque, error = self.get_bloque_or_404(pk)
        if error:
            return error

        serializer = BloqueHorarioUpdateSerializer(
            bloque, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        try:
            bloque = BloqueHorarioService.actualizar_bloque(
                bloque, serializer.validated_data
            )
        except ColisionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_409_CONFLICT)

        # FIX P2: re-fetch con select_related para evitar N+1 en la serialización
        bloque = BloqueHorario.objects.select_related(
            'aula', 'docente__user', 'ficha__version__programa', 'competencia'
        ).get(pk=bloque.pk)

        return Response(BloqueHorarioDetailSerializer(bloque).data)