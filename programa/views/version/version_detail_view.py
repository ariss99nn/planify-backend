from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from programa.serializers.version.version_detail_serializer import VersionDetailSerializer
from programa.views.programa_base_view import ProgramaBaseView
from ficha.models.ficha_model import Ficha
from users.models.user import User


class VersionDetailView(ProgramaBaseView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        version, error = self.get_version_or_404(pk)
        if error:
            return error

        if request.user.rol == User.Rol.ESTUDIANTE:
            tiene_ficha = Ficha.objects.filter(
                estado=Ficha.Estado.ACTIVA,
                version=version,
            ).exists()
            if not tiene_ficha:
                return Response(
                    {'detail': 'No tienes acceso a esta versión.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(VersionDetailSerializer(version).data)