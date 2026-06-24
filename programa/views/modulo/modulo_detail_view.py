from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from programa.serializers.modulo.modulo_detail_serializer import ModuloDetailSerializer
from programa.views.programa_base_view import ProgramaBaseView
from ficha.models.ficha_model import Ficha
from users.models.user import User


class ModuloDetailView(ProgramaBaseView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        modulo, error = self.get_modulo_or_404(pk)
        if error:
            return error

        if request.user.rol == User.Rol.ESTUDIANTE:
            tiene_ficha = Ficha.objects.filter(
                estado=Ficha.Estado.ACTIVA,
                version=modulo.version,
            ).exists()
            if not tiene_ficha:
                return Response(
                    {'detail': 'No tienes acceso a este módulo.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(ModuloDetailSerializer(modulo).data)