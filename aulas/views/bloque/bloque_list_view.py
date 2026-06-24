from rest_framework.permissions import IsAuthenticated
from users.permissions import IsStaffLike
from rest_framework.response import Response
from aulas.models.bloque_model import Bloque
from aulas.serializers import BloqueListSerializer
from aulas.filters.aula_filter import BloqueFilter
from aulas.filters.aula_pagination import AulaPagination 
from aulas.views.aula_base_view import AulaBaseView


class BloqueListView(AulaBaseView):
    permission_classes = [IsAuthenticated, IsStaffLike]

    def get(self, request):
        queryset  = Bloque.objects.all()
        filterset = BloqueFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        paginator = AulaPagination()
        page = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            BloqueListSerializer(page, many=True).data
        )