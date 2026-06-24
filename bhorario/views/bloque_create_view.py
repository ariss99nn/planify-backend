# bhorario/views/bloque_create_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bhorario.views.bhorario_base import BhorarioBaseView
from bhorario.permissions.bhorario_permissions import CanManageHorario
from bhorario.serializers import BloqueHorarioCreateSerializer, BloqueHorarioDetailSerializer
from bhorario.services.bloque_service import BloqueHorarioService, ColisionError
from bhorario.models.bloque_horario_model import BloqueHorario


class BloqueHorarioCreateView(BhorarioBaseView):
    permission_classes = [IsAuthenticated, CanManageHorario]

    def post(self, request):
        serializer = BloqueHorarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            bloque = BloqueHorarioService.crear_bloque(serializer.validated_data)
        except ColisionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_409_CONFLICT)

        # FIX P1: re-fetch con select_related para evitar N+1 en la serialización
        bloque = BloqueHorario.objects.select_related(
            'aula', 'docente__user', 'ficha__version__programa', 'competencia'
        ).get(pk=bloque.pk)

        return Response(
            BloqueHorarioDetailSerializer(bloque).data,
            status=status.HTTP_201_CREATED,
        )