# ficha/views/reasignacion/reasignacion_list_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ficha.models.ficha_reasignacion_model import ReasignacionFicha
from ficha.serializers import ReasignacionListSerializer
from ficha.filter.ficha_filter import ReasignacionFilter
from ficha.filter.ficha_pagination import FichaPagination
from users.permissions import IsManager
from ficha.views.ficha_base_view import FichaBaseView

class ReasignacionListView(FichaBaseView):
    """GET /api/fichas/reasignaciones/ — solo IsManager."""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        queryset = ReasignacionFicha.objects.select_related(
            'estudiante',
            'ficha_origen__version__programa',
            'ficha_destino__version__programa',
            'realizado_por',
        )
        filterset = ReasignacionFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        paginator = FichaPagination()
        page = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            ReasignacionListSerializer(page, many=True).data
        )