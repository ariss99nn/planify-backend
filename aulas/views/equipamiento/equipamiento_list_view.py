from rest_framework.permissions import IsAuthenticated
from users.permissions import IsStaffLike
from rest_framework.response import Response
from aulas.models.equipamiento_model import Equipamiento
from aulas.serializers import EquipamientoListSerializer
from aulas.filters.aula_filter import EquipamientoFilter
from aulas.filters.aula_pagination import AulaPagination 
from aulas.views.aula_base_view import AulaBaseView

class EquipamientoListView(AulaBaseView):
    permission_classes = [IsAuthenticated, IsStaffLike]

    def get(self, request):
        queryset  = Equipamiento.objects.all()
        filterset = EquipamientoFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        paginator = AulaPagination()
        page = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            EquipamientoListSerializer(page, many=True).data
        )