from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from competencia.models.asignatura_model import Asignatura
from competencia.serializers.asignatura.asignatura_list_serializer import AsignaturaListSerializer
from competencia.filters.competencia_filters import AsignaturaFilter
from competencia.filters.competencia_pagination import CompetenciaPagination
from competencia.permissions.competencia_permissions import CanManageCompetencia
from competencia.views.competencia_base_view import CompetenciaBaseView
from ficha.models.ficha_model import Ficha
from users.models.user import User


class AsignaturaListView(CompetenciaBaseView):
    permission_classes = [IsAuthenticated, CanManageCompetencia]

    def get_queryset(self, request):
        user = request.user
        qs = Asignatura.objects.select_related('modulo__version__programa')

        if user.rol in {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO}:
            return qs

        if user.rol == User.Rol.DOCENTE:
            if not hasattr(user, 'docente'):
                return qs.none()
            from docentes.models.docente_habilitacion_model import HabilitacionDocente
            docente = user.docente
            asignatura_ids = HabilitacionDocente.objects.filter(
                docente=docente,
                nivel=HabilitacionDocente.Nivel.ASIGNATURA,
                activo=True,
            ).values_list('asignatura_id', flat=True)
            modulo_ids = HabilitacionDocente.objects.filter(
                docente=docente,
                nivel=HabilitacionDocente.Nivel.MODULO,
                activo=True,
            ).values_list('modulo_id', flat=True)
            return qs.filter(
                Q(pk__in=asignatura_ids) | Q(modulo_id__in=modulo_ids)
            ).distinct()

        if user.rol == User.Rol.ESTUDIANTE:
            modulo_ids = Ficha.objects.filter(
                estado=Ficha.Estado.ACTIVA,
            ).values_list('version__modulos__id', flat=True).distinct()
            return qs.filter(modulo_id__in=modulo_ids)

        return qs.none()

    def get(self, request):
        queryset = self.get_queryset(request)
        filterset = AsignaturaFilter(request.GET, queryset=queryset)
        paginator = CompetenciaPagination()
        page = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            AsignaturaListSerializer(page, many=True).data
        )