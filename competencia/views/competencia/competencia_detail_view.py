from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from competencia.models.competencia_model import Competencia
from competencia.serializers.competencia.competencia_detail_serializer import CompetenciaDetailSerializer
from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView
from ficha.models.ficha_model import Ficha
from users.models.user import User


class CompetenciaDetailView(CompetenciaBaseView):
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def get(self, request, pk):
        competencia, error = self.get_competencia_or_404(pk)
        if error:
            return error

        user = request.user

        # Transversales: pertenecen al centro, visibles para cualquier rol
        # habilitado por CanManageCompetencia.
        if competencia.tipo == Competencia.TipoCompetencia.TRANSVERSAL:
            return Response(CompetenciaDetailSerializer(competencia).data)

        if user.rol == User.Rol.DOCENTE:
            if not hasattr(user, 'docente'):
                return Response(
                    {'detail': 'No tienes acceso a esta competencia.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            from docentes.models.docente_habilitacion_model import HabilitacionDocente
            tiene_acceso = HabilitacionDocente.objects.filter(
                docente=user.docente,
                activo=True,
            ).filter(
                Q(asignatura=competencia.asignatura) |
                Q(modulo=competencia.asignatura.modulo)
            ).exists()
            if not tiene_acceso:
                return Response(
                    {'detail': 'No tienes acceso a esta competencia.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if user.rol == User.Rol.ESTUDIANTE:
            tiene_ficha = Ficha.objects.filter(
                estado=Ficha.Estado.ACTIVA,
                version__modulos=competencia.asignatura.modulo,
            ).exists()
            if not tiene_ficha:
                return Response(
                    {'detail': 'No tienes acceso a esta competencia.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(CompetenciaDetailSerializer(competencia).data)