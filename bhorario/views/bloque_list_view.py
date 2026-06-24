# bhorario/views/bloque_list_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bhorario.views.bhorario_base import BhorarioBaseView          # FIX B15
from bhorario.models.bloque_horario_model import BloqueHorario
from bhorario.serializers import BloqueHorarioListSerializer
from bhorario.filters import BloqueHorarioFilter, BhorarioPagination
from users.models.user import User


class BloqueHorarioListView(BhorarioBaseView):
    """
    GET /api/horarios/
    - Gestión (coordinador / administrativo): todos los bloques.
    - Docente: solo sus bloques asignados.
    - Estudiante: bloques de su(s) ficha(s) activa(s).
    """
    permission_classes = [IsAuthenticated]

    def _get_queryset(self, request):
        user = request.user
        qs   = BloqueHorario.objects.select_related(
            'aula', 'docente__user', 'ficha__version__programa'
        )

        if user.rol in {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO}:
            return qs

        if user.rol == User.Rol.DOCENTE:
            return qs.filter(docente__user=user)

        if user.rol == User.Rol.ESTUDIANTE:
            from ficha.models.ficha_estudiante_model import FichaEstudiante
            ficha_ids = FichaEstudiante.objects.filter(
                estudiante=user, activo=True
            ).values_list('ficha_id', flat=True)
            return qs.filter(ficha_id__in=ficha_ids)

        return qs.none()

    def get(self, request):
        queryset  = self._get_queryset(request)
        filterset = BloqueHorarioFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        paginator = BhorarioPagination()
        page      = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            BloqueHorarioListSerializer(page, many=True).data
        )