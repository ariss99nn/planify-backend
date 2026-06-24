# reportes/views/reporte_solicitar_view.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from reportes.models.reporte_generado_model import ReporteGenerado
from reportes.serializers.reporte_generado_serializer import (
    ReporteGeneradoCreateSerializer,
    ReporteGeneradoListSerializer,
)
from reportes.permissions.reportes_permissions import ROLES_GESTION
from reportes.tasks.reportes_tasks import generar_reporte


class SolicitarReporteView(APIView):
    """
    POST /api/reportes/solicitar/
    Gestión: cualquier tipo registrado en el factory.
    Docente: solo FICHAS y HORARIOS (validado en el serializer).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReporteGeneradoCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        reporte = ReporteGenerado.objects.create(
            tipo=serializer.validated_data['tipo'],
            filtros=serializer.validated_data.get('filtros', {}),
            usuario=request.user,
        )

        task = generar_reporte.delay(reporte_id=reporte.pk)
        reporte.tarea_id = task.id
        reporte.save(update_fields=['tarea_id', 'updated_at'])

        return Response(
            ReporteGeneradoListSerializer(reporte, context={'request': request}).data,
            status=status.HTTP_202_ACCEPTED,
        )


class EstadoReporteView(APIView):
    """GET /api/reportes/{id}/ — consulta estado/resultado de un reporte."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        qs = ReporteGenerado.objects.filter(pk=pk)
        if request.user.rol not in ROLES_GESTION:
            qs = qs.filter(usuario=request.user)

        reporte = qs.first()
        if not reporte:
            return Response(
                {'detail': 'Reporte no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            ReporteGeneradoListSerializer(reporte, context={'request': request}).data
        )