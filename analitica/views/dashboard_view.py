# analitica/views/dashboard_view.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from analitica.models.analitica_snapshot_model import AnaliticaSnapshot
from analitica.permissions.analitica_permissions import CanViewAnalitica
from analitica.serializers.snapshot_serializer import SnapshotProgramaSerializer
from alertas.models.alerta_model import Alerta


class DashboardView(APIView):
    """
    GET /api/analitica/
    Retorna el último snapshot + alertas críticas en tiempo real.
    La mayor parte de los datos viene del snapshot pre-agregado
    para mantener la respuesta rápida.
    """
    permission_classes = [IsAuthenticated, CanViewAnalitica]

    def get(self, request):
        try:
            snapshot = AnaliticaSnapshot.objects.latest()
            data = {
                'fecha_snapshot': snapshot.fecha,
                'fichas': {
                    'activas':    snapshot.fichas_activas,
                    'lectiva':    snapshot.fichas_lectiva,
                    'productiva': snapshot.fichas_productiva,
                },
                'estudiantes': {
                    'activos':          snapshot.estudiantes_activos,
                    'deserciones_mes':  snapshot.deserciones_mes,
                    'graduados_mes':    snapshot.graduados_mes,
                    'reasignaciones_mes': snapshot.reasignaciones_mes,
                },
                'docentes': {
                    'activos':       snapshot.docentes_activos,
                    'sobrecargados': snapshot.docentes_sobrecargados,
                },
                'aulas': {
                    'activas':      snapshot.aulas_activas,
                    'mantenimiento': snapshot.aulas_mantenimiento,
                    'inactivas':    snapshot.aulas_inactivas,
                },
                'planes': {
                    'aprobados': snapshot.planes_aprobados,
                    'pendientes': snapshot.planes_pendientes,
                },
                'alertas': {
                    'pendientes':    snapshot.alertas_pendientes,
                    'conflictos_mes': snapshot.conflictos_horario_mes,
                },
                'breakdown_programas': SnapshotProgramaSerializer(
                    snapshot.programas.select_related('programa').all(),
                    many=True,
                ).data,
                # Alertas críticas en tiempo real (no del snapshot) —
                # los 5 conflictos más recientes sin resolver.
                'alertas_criticas': list(
                    Alerta.objects.filter(
                        estado=Alerta.EstadoAlerta.PENDIENTE,
                        tipo=Alerta.TipoAlerta.CONFLICTO,
                    ).values('id', 'descripcion', 'fecha_creacion')
                    .order_by('-fecha_creacion')[:5]
                ),
            }
        except AnaliticaSnapshot.DoesNotExist:
            data = {'mensaje': 'No hay snapshots generados aún. Ejecuta la tarea Celery.'}

        return Response(data)