# planificacion/views/item_plan_views.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from planificacion.filters.planificacion_filters import ItemPlanFilter
from planificacion.filters.planificacion_pagination import PlanificacionPagination
from planificacion.models.item_plan_model import ItemPlan
from planificacion.permissions import CanManagePlan
from planificacion.serializers.item_plan_serializer import (
    ItemPlanCreateSerializer,
    ItemPlanListSerializer,
    ItemPlanUpdateSerializer,
)
from planificacion.views.planificacion_base_view import PlanificacionBaseView


class ItemPlanListView(PlanificacionBaseView):
    """GET /api/items/"""
    permission_classes = [IsAuthenticated, CanManagePlan]

    def get(self, request):
        queryset  = ItemPlan.objects.select_related(
            'competencia', 'docente__user', 'plan__ficha'
        )
        filterset = ItemPlanFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        paginator = PlanificacionPagination()
        page      = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            ItemPlanListSerializer(page, many=True).data
        )


class ItemPlanCreateView(PlanificacionBaseView):
    """POST /api/items/create/"""
    permission_classes = [IsAuthenticated, CanManagePlan]

    def post(self, request):
        serializer = ItemPlanCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return Response(
            ItemPlanListSerializer(item).data,
            status=status.HTTP_201_CREATED,
        )


class ItemPlanUpdateView(PlanificacionBaseView):
    """PATCH /api/items/{id}/update/"""
    permission_classes = [IsAuthenticated, CanManagePlan]

    def patch(self, request, pk):
        item, error = self.get_item_or_404(pk)
        if error:
            return error
        self.check_object_permissions(request, item.plan)

        serializer = ItemPlanUpdateSerializer(
            item, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # CORRECCIÓN: refresh para que los properties calculados sean actuales
        item.refresh_from_db()
        return Response(ItemPlanListSerializer(item).data)