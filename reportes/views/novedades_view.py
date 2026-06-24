# reportes/views/novedad_views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from reportes.models.novedad_model import Novedad
from reportes.serializers.novedad_serializer import (
    NovedadListSerializer,
    NovedadCreateSerializer,
    NovedadAtenderSerializer,
)
from reportes.permissions.reportes_permissions import CanManageNovedad


class NovedadPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NovedadListView(generics.ListAPIView):
    """GET /api/novedades/ — solo gestión."""
    permission_classes = [IsAuthenticated, CanManageNovedad]
    serializer_class = NovedadListSerializer
    pagination_class = NovedadPagination

    def get_queryset(self):
        qs = Novedad.objects.select_related(
            'atendida_por', 'generada_por'
        ).order_by('prioridad', '-fecha_generacion')

        atendida = self.request.query_params.get('atendida')
        tipo = self.request.query_params.get('tipo')
        if atendida is not None:
            qs = qs.filter(atendida=atendida.lower() == 'true')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs


class NovedadCreateView(APIView):
    """POST /api/novedades/crear/ — solo gestión, novedades manuales."""
    permission_classes = [IsAuthenticated, CanManageNovedad]

    def post(self, request):
        serializer = NovedadCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        novedad = serializer.save()
        return Response(
            NovedadListSerializer(novedad).data,
            status=status.HTTP_201_CREATED,
        )


class NovedadAtenderView(APIView):
    """PATCH /api/novedades/{id}/atender/ — solo gestión."""
    permission_classes = [IsAuthenticated, CanManageNovedad]

    def patch(self, request, pk):
        novedad = Novedad.objects.filter(pk=pk).first()
        if novedad is None:
            return Response(
                {'detail': 'Novedad no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if novedad.atendida:
            return Response(
                {'detail': 'Esta novedad ya fue atendida previamente.'},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = NovedadAtenderSerializer(
            novedad, data=request.data,
            partial=True, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        novedad = serializer.save()
        return Response(NovedadListSerializer(novedad).data)