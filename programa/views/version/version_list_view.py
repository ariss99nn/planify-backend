# programa/views/version/version_list_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from programa.models.version_programa_model import VersionPrograma
from programa.serializers.version.version_list_serializer import VersionListSerializer
from programa.filters.programa_filters import VersionFilter
from programa.filters.programa_pagination import ProgramaPagination
from programa.views.programa_base_view import ProgramaBaseView
from ficha.models.ficha_model import Ficha
from users.models.user import User


class VersionListView(ProgramaBaseView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        user = request.user
        qs = VersionPrograma.objects.select_related('programa')

        if user.rol in {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO, User.Rol.DOCENTE}:
            return qs

        if user.rol == User.Rol.ESTUDIANTE:
            version_ids = Ficha.objects.filter(
                estado=Ficha.Estado.ACTIVA,
            ).values_list('version_id', flat=True).distinct()
            return qs.filter(pk__in=version_ids)

        return qs.none()

    def get(self, request):
        queryset = self.get_queryset(request)
        filterset = VersionFilter(request.GET, queryset=queryset)
        paginator = ProgramaPagination()
        page = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            VersionListSerializer(page, many=True).data
        )