# ficha/views/historial/historial_list_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ficha.serializers import HistorialEtapaListSerializer
from users.permissions import IsManager
from ficha.models.ficha_historial_etapa_model import HistorialEtapa
from ficha.filter.ficha_filter import HistorialEtapaFilter
from ficha.filter.ficha_pagination import FichaPagination
from ficha.views.ficha_base_view import FichaBaseView


class HistorialEtapaListView(FichaBaseView):
    """
    GET /api/fichas/historial/
    Solo IsManager. Soporta filtros por ficha, etapa_nueva, etapa_anterior.
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        queryset = HistorialEtapa.objects.select_related(
            'ficha__version__programa',
            'cambiado_por',
        )
        filterset = HistorialEtapaFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)

        paginator = FichaPagination()
        page = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            HistorialEtapaListSerializer(page, many=True).data
        )