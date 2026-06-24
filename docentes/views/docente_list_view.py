# docentes/views/docente_list_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from docentes.models.docente_model import Docente
from docentes.permissions.docente_permissions import CanManageDocente
from docentes.serializers.docente_list_serializer import DocenteListSerializer
from docentes.filters.docente_filter import DocenteFilter
from docentes.filters.docente_pagination import DocentePagination
from docentes.views.docente_base_view import DocenteBaseView

class DocenteListView(DocenteBaseView):
    permission_classes = [IsAuthenticated, CanManageDocente]

    def get(self, request):
        queryset = Docente.objects.select_related('user').order_by(
            'user__apellido', 'user__nombre'
        )

        filterset = DocenteFilter(request.GET, queryset=queryset, request=request)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)

        paginator = DocentePagination()
        page = paginator.paginate_queryset(filterset.qs, request)
        serializer = DocenteListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)