# exportacion/views/exportacion_view.py
import logging

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from exportacion.serializers.exportacion_request_serializer import ExportacionRequestSerializer
from exportacion.services.exportacion_service import ExportacionService
from exportacion.models.exportacion_model import RegistroExportacion
from exportacion.permissions.exportacion_permissions import CanExport
from core.shared.utils import get_ip_from_request

logger = logging.getLogger(__name__)


class ExportarView(APIView):
    """
    POST /api/exportar/
    Solo COORDINADOR y ADMINISTRATIVO.
    Genera y descarga el archivo directamente (sin Celery).
    Registra auditoría en RegistroExportacion solo en caso de éxito.
    """
    permission_classes = [IsAuthenticated, CanExport]

    def post(self, request):
        serializer = ExportacionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modulo  = serializer.validated_data["modulo"]
        formato = serializer.validated_data["formato"]
        filtros = serializer.validated_data.get("filtros", {})
        filtros = {k: v for k, v in filtros.items() if v not in ("", None)}

        try:
            headers, rows = ExportacionService.exportar(modulo, filtros)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception(
                "Fallo al exportar módulo=%s formato=%s usuario=%s",
                modulo, formato, request.user.pk,
            )
            return Response(
                {"detail": "Error interno al generar la exportación."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if formato == RegistroExportacion.Formato.CSV:
            contenido    = ExportacionService.a_csv(headers, rows)
            content_type = "text/csv; charset=utf-8"
            extension    = "csv"
        else:
            contenido    = ExportacionService.a_excel(headers, rows)
            content_type = (
                "application/vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            )
            extension = "xlsx"

        nombre_archivo = f"{modulo.lower()}_{request.user.pk}.{extension}"
        response = HttpResponse(contenido, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'

        RegistroExportacion.objects.create(
            usuario=request.user,
            tipo=modulo,
            formato=formato,
            filtros=filtros,
            registros_exportados=len(rows),
            ip_origen=get_ip_from_request(request),
        )

        return response