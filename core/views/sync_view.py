from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta


class SyncView(APIView):
    """
    GET /api/sync/?since=<ISO8601>
    Retorna todos los datos modificados desde una fecha.
    Flutter puede llamar esto al reconectar después de estar offline.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        since_str = request.query_params.get('since')
        if since_str:
            try:
                from dateutil.parser import parse
                since = parse(since_str)
            except Exception:
                since = timezone.now() - timedelta(hours=24)
        else:
            since = timezone.now() - timedelta(hours=24)

        user = request.user
        data = {'since': since.isoformat(), 'timestamp': timezone.now().isoformat()}

        # Datos del usuario según su rol
        if hasattr(user, 'docente'):
            from bhorario.models.bloque_horario_model import BloqueHorario
            from bhorario.serializers import BloqueHorarioListSerializer
            bloques = BloqueHorario.objects.filter(
                docente__user=user,
                # updated_at__gte=since  # si agregas updated_at
            )
            data['bloques_horario'] = BloqueHorarioListSerializer(
                bloques, many=True
            ).data

        from alertas.models.alerta_model import Alerta
        from alertas.serializers import AlertaListSerializer
        alertas = Alerta.objects.filter(
            destinatario=user,
            estado=Alerta.EstadoAlerta.PENDIENTE,
        )
        data['alertas_pendientes'] = AlertaListSerializer(alertas, many=True).data
        data['total_alertas'] = alertas.count()

        return Response(data)