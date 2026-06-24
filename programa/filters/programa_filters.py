# programa/filters/programa_filters.py
import django_filters
from django.db.models import Q
from programa.models.programa_model import Programa
from programa.models.version_programa_model import VersionPrograma
from programa.models.modulo_model import Modulo


class ProgramaFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search', label='Búsqueda'
    )
    nivel = django_filters.ChoiceFilter(choices=Programa.Nivel.choices)
    estado = django_filters.ChoiceFilter(choices=Programa.Estado.choices)

    class Meta:
        model = Programa
        fields = ['nivel', 'estado']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(descripcion__icontains=value)
        )


class VersionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search', label='Búsqueda'
    )
    programa = django_filters.ModelChoiceFilter(
        queryset=Programa.objects.all()
    )
    vigente = django_filters.BooleanFilter()

    class Meta:
        model = VersionPrograma
        fields = ['programa', 'vigente']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(programa__nombre__icontains=value) |
            Q(descripcion__icontains=value)
        )


class ModuloFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search', label='Búsqueda'
    )
    version = django_filters.ModelChoiceFilter(
        queryset=VersionPrograma.objects.all()
    )
    estado = django_filters.ChoiceFilter(choices=Modulo.Estado.choices)

    class Meta:
        model = Modulo
        fields = ['version', 'estado']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(descripcion__icontains=value)
        )