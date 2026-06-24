# bhorario/views/horario_semanal_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bhorario.models.bloque_horario_model import BloqueHorario
from bhorario.serializers import BloqueHorarioListSerializer
from users.models.user import User


class HorarioSemanalView(APIView):
    """
    GET /api/horarios/semanal/
    Parámetros opcionales (solo gestión): ?docente=<id>&aula=<id>&ficha=<id>&jornada=<valor>
    Devuelve los bloques organizados por día de la semana.
    """
    permission_classes = [IsAuthenticated]

    ORDEN_DIAS = [
        BloqueHorario.DiaSemana.LUNES,
        BloqueHorario.DiaSemana.MARTES,
        BloqueHorario.DiaSemana.MIERCOLES,
        BloqueHorario.DiaSemana.JUEVES,
        BloqueHorario.DiaSemana.VIERNES,
        BloqueHorario.DiaSemana.SABADO,
    ]

    _ROLES_GESTION = {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO}

    # FIX B2: convierte un query param a int de forma segura
    @staticmethod
    def _safe_int(value: str | None) -> int | None:
        if not value:
            return None
        try:
            n = int(value)
            return n if n > 0 else None
        except (ValueError, TypeError):
            return None

    def _get_queryset(self, request):
        user = request.user
        qs   = BloqueHorario.objects.select_related(
            'aula', 'docente__user', 'ficha__version__programa'
        )

        # Restricción por rol PRIMERO — no puede ser sobrescrita por query params
        if user.rol == User.Rol.DOCENTE:
            return qs.filter(docente__user=user)

        if user.rol == User.Rol.ESTUDIANTE:
            from ficha.models.ficha_estudiante_model import FichaEstudiante
            ficha_ids = FichaEstudiante.objects.filter(
                estudiante=user, activo=True
            ).values_list('ficha_id', flat=True)
            return qs.filter(ficha_id__in=ficha_ids)

        # Gestión: aplica filtros opcionales validando tipos — FIX B2
        if user.rol in self._ROLES_GESTION:
            docente_id = self._safe_int(request.query_params.get('docente'))
            aula_id    = self._safe_int(request.query_params.get('aula'))
            ficha_id   = self._safe_int(request.query_params.get('ficha'))
            jornada    = request.query_params.get('jornada')

            if docente_id:
                qs = qs.filter(docente_id=docente_id)
            if aula_id:
                qs = qs.filter(aula_id=aula_id)
            if ficha_id:
                qs = qs.filter(ficha_id=ficha_id)
            if jornada and jornada in BloqueHorario.Jornada.values:
                qs = qs.filter(jornada=jornada)

            return qs

        return qs.none()

    def get(self, request):
        qs      = self._get_queryset(request)
        bloques = list(qs.order_by('orden_dia', 'hora_inicio'))

        horario = {}
        for dia in self.ORDEN_DIAS:
            bloques_dia = [b for b in bloques if b.dia_semana == dia]
            if bloques_dia:
                horario[dia] = {
                    'dia_display': dict(BloqueHorario.DiaSemana.choices)[dia],
                    'bloques':     BloqueHorarioListSerializer(
                        bloques_dia, many=True
                    ).data,
                }

        return Response({
            'total_bloques': len(bloques),
            'dias':          horario,
        })