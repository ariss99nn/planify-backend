# exportacion/views/registro_exportacion_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from exportacion.models.exportacion_model import RegistroExportacion
from exportacion.serializers.registro_exportacion_serializer import RegistroExportacionSerializer
from exportacion.permissions.exportacion_permissions import CanViewRegistroExportacion


class RegistroExportacionListView(APIView):
    """
    GET /api/exportaciones/log/
    Solo lectura — COORDINADOR y ADMINISTRATIVO.
    Soporta filtros por ?tipo=FICHAS y ?usuario=<id>.
    Paginado: ?page=1&page_size=20 (máx. 100).
    """
    permission_classes = [IsAuthenticated, CanViewRegistroExportacion]

    def get(self, request):
        qs = RegistroExportacion.objects.select_related("usuario").order_by("-fecha")

        tipo       = request.query_params.get("tipo")
        usuario_id = request.query_params.get("usuario")
        if tipo:
            qs = qs.filter(tipo=tipo)
        if usuario_id:
            qs = qs.filter(usuario_id=usuario_id)

        paginator = _LogPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = RegistroExportacionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class _LogPagination(PageNumberPagination):
    page_size               = 20
    page_size_query_param   = "page_size"
    max_page_size           = 100