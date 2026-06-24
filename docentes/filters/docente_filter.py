# docentes/filters/docente_filter.py
import django_filters
from django.db.models import Q
from docentes.models.docente_model import Docente
class DocenteFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search',
        label='Búsqueda general',
    )
    estado = django_filters.BooleanFilter()
    especialidad = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Especialidad',
    )

    class Meta:
        model = Docente
        fields = ['estado', 'especialidad']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(user__nombre__icontains=value) |
            Q(user__email__icontains=value) |
            Q(especialidad__icontains=value)
        )