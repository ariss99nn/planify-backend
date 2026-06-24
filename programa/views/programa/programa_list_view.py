from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from programa.models.programa_model import Programa
from programa.serializers.programa.programa_list_serializer import ProgramaListSerializer
from programa.filters.programa_filters import ProgramaFilter
from programa.filters.programa_pagination import ProgramaPagination
from programa.views.programa_base_view import ProgramaBaseView
from ficha.models.ficha_model import Ficha
from users.models.user import User

class ProgramaListView(ProgramaBaseView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        # prefetch_related evita N+1 cuando el serializer llama versiones.count()
        base_qs = Programa.objects.prefetch_related('versiones')

        user = request.user
        if user.rol in {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO, User.Rol.DOCENTE}:
            return base_qs.all()

        if user.rol == User.Rol.ESTUDIANTE:
            programa_ids = Ficha.objects.filter(
                estado=Ficha.Estado.ACTIVA,
            ).values_list('version__programa_id', flat=True).distinct()
            return base_qs.filter(pk__in=programa_ids)

        return Programa.objects.none()

    def get(self, request):
        queryset  = self.get_queryset(request)
        filterset = ProgramaFilter(request.GET, queryset=queryset)
        paginator = ProgramaPagination()
        page      = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            ProgramaListSerializer(page, many=True).data
        )
