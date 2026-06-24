#alertas/filters/alerta_filter.py
import django_filters
from alertas.models.alerta_model import Alerta

class AlertaFilter(django_filters.FilterSet):
    """
    Filtros disponibles en GET /api/alertas/:

      ?tipo=CONFLICTO|DISPONIBILIDAD|SISTEMA
      ?estado=PENDIENTE|ENVIADA|LEIDA
      ?solo_no_leidas=true          → excluye LEIDA
      ?bloque_origen=<pk>
      ?fecha_desde=2024-01-01T00:00
      ?fecha_hasta=2024-12-31T23:59
    """
    solo_no_leidas = django_filters.BooleanFilter(
        method='filter_no_leidas',
        label='Solo no leídas',
    )
    fecha_desde = django_filters.DateTimeFilter(
        field_name='fecha_creacion',
        lookup_expr='gte',
    )
    fecha_hasta = django_filters.DateTimeFilter(
        field_name='fecha_creacion',
        lookup_expr='lte',
    )
    class Meta:
        model  = Alerta
        fields = ['tipo', 'estado', 'bloque_origen']

    def filter_no_leidas(self, queryset, name, value):
        if value:
            return queryset.exclude(estado=Alerta.EstadoAlerta.LEIDA)
        return queryset


