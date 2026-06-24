import django_filters
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from aulas.models.aula_model import Aula
from aulas.models.equipamiento_model import Equipamiento
from aulas.models.bloque_model import Bloque

class AulaFilter(django_filters.FilterSet):
    search       = django_filters.CharFilter(method='filter_search', label='Búsqueda')
    estado       = django_filters.ChoiceFilter(choices=Aula.Estado.choices)
    tipo_aula    = django_filters.ChoiceFilter(choices=Aula.TipoAula.choices)
    bloque       = django_filters.ModelChoiceFilter(queryset=Bloque.objects.all())
    capacidad_min = django_filters.NumberFilter(
        field_name='capacidad', lookup_expr='gte', label='Capacidad mínima'
    )

    class Meta:
        model  = Aula
        fields = ['estado', 'tipo_aula', 'bloque']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(codigo_aula__icontains=value)
            | Q(bloque__nombre__icontains=value)
            | Q(descripcion__icontains=value)
        )


class EquipamientoFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Búsqueda')
    estado = django_filters.ChoiceFilter(choices=Equipamiento.Estado.choices)

    class Meta:
        model  = Equipamiento
        fields = ['estado']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(nombre__icontains=value)
            | Q(descripcion__icontains=value)
            | Q(numero_serie__icontains=value)
        )


class BloqueFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Búsqueda')
    estado = django_filters.ChoiceFilter(choices=Bloque.Estado.choices)

    class Meta:
        model  = Bloque
        fields = ['estado']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(nombre__icontains=value)
            | Q(descripcion__icontains=value)
        )