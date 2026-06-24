# programa/views/modulo/modulo_list_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from programa.models.modulo_model import Modulo
from programa.serializers.modulo.modulo_list_serializer import ModuloListSerializer
from programa.filters.programa_filters import ModuloFilter
from programa.filters.programa_pagination import ProgramaPagination
from programa.views.programa_base_view import ProgramaBaseView
from ficha.models.ficha_model import Ficha
from users.models.user import User


class ModuloListView(ProgramaBaseView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        user = request.user
        qs = Modulo.objects.select_related('version__programa')

        if user.rol in {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO, User.Rol.DOCENTE}:
            return qs

        if user.rol == User.Rol.ESTUDIANTE:
            version_ids = Ficha.objects.filter(
                estado=Ficha.Estado.ACTIVA,
            ).values_list('version_id', flat=True).distinct()
            return qs.filter(version_id__in=version_ids)

        return qs.none()

    def get(self, request):
        queryset = self.get_queryset(request)
        filterset = ModuloFilter(request.GET, queryset=queryset)
        paginator = ProgramaPagination()
        page = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            ModuloListSerializer(page, many=True).data
        )