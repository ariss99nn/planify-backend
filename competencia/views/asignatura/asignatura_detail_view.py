from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from competencia.serializers.asignatura.asignatura_detail_serializer import AsignaturaDetailSerializer
from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView
from ficha.models.ficha_model import Ficha
from users.models.user import User


class AsignaturaDetailView(CompetenciaBaseView):
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def get(self, request, pk):
        asignatura, error = self.get_asignatura_or_404(pk)
        if error:
            return error

        user = request.user

        if user.rol == User.Rol.DOCENTE:
            if not hasattr(user, 'docente'):
                return Response(
                    {'detail': 'No tienes acceso a esta asignatura.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            from docentes.models.docente_habilitacion_model import HabilitacionDocente
            tiene_acceso = HabilitacionDocente.objects.filter(
                docente=user.docente,
                activo=True,
            ).filter(
                Q(asignatura=asignatura) | Q(modulo=asignatura.modulo)
            ).exists()
            if not tiene_acceso:
                return Response(
                    {'detail': 'No tienes acceso a esta asignatura.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if user.rol == User.Rol.ESTUDIANTE:
            tiene_ficha = Ficha.objects.filter(
                estado=Ficha.Estado.ACTIVA,
                version__modulos=asignatura.modulo,
            ).exists()
            if not tiene_ficha:
                return Response(
                    {'detail': 'No tienes acceso a esta asignatura.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(AsignaturaDetailSerializer(asignatura).data)