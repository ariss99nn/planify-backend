# bhorario/views/bloque_delete_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bhorario.views.bhorario_base import BhorarioBaseView
from bhorario.permissions.bhorario_permissions import CanManageHorario


class BloqueHorarioDeleteView(BhorarioBaseView):
    permission_classes = [IsAuthenticated, CanManageHorario]

    def delete(self, request, pk):
        bloque, error = self.get_bloque_or_404(pk)
        if error:
            return error
        bloque.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)