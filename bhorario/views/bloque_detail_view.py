# bhorario/views/bloque_detail_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from bhorario.views.bhorario_base import BhorarioBaseView
from bhorario.serializers import BloqueHorarioDetailSerializer
from users.models.user import User


class BloqueHorarioDetailView(BhorarioBaseView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        bloque, error = self.get_bloque_or_404(pk)
        if error:
            return error

        user = request.user

        if user.rol == User.Rol.DOCENTE:
            if not (bloque.docente and bloque.docente.user == user):
                return Response(
                    {'detail': 'No tienes acceso a este bloque.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if user.rol == User.Rol.ESTUDIANTE:
            # FIX B3: si el bloque no tiene ficha asignada, el estudiante
            # no puede acceder — evita filter(ficha=None) que sería incorrecto.
            if bloque.ficha_id is None:
                return Response(
                    {'detail': 'No tienes acceso a este bloque.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            from ficha.models.ficha_estudiante_model import FichaEstudiante
            if not FichaEstudiante.objects.filter(
                estudiante=user,
                ficha_id=bloque.ficha_id,   # usa el ID directamente, evita lazy-load
                activo=True,
            ).exists():
                return Response(
                    {'detail': 'No tienes acceso a este bloque.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(BloqueHorarioDetailSerializer(bloque).data)