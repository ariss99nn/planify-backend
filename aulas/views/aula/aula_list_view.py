from rest_framework.permissions import IsAuthenticated
from users.permissions import IsStaffLike
from rest_framework.response import Response
from aulas.models.aula_model import Aula
from aulas.serializers import AulaListSerializer
from aulas.filters.aula_filter import AulaFilter
from aulas.filters.aula_pagination import AulaPagination 
from aulas.views.aula_base_view import AulaBaseView

class AulaListView(AulaBaseView):
    permission_classes = [IsAuthenticated, IsStaffLike]

    def get(self, request):
        queryset = (
            Aula.objects
            .select_related('bloque')
            .prefetch_related('equipamiento')
            .all()
        )
        filterset = AulaFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        paginator = AulaPagination()
        page = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            AulaListSerializer(page, many=True).data
        )