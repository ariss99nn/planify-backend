import django_filters
from django.db.models import Q
from competencia.models.asignatura_model import Asignatura
from competencia.models.competencia_model import Competencia
from competencia.models.resultado_aprendizaje_model import ResultadoAprendizaje


class AsignaturaFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search', label='Búsqueda'
    )
    modulo = django_filters.NumberFilter(field_name='modulo__id')
    tipo = django_filters.ChoiceFilter(choices=Asignatura.Tipo.choices)
    estado = django_filters.ChoiceFilter(choices=Asignatura.Estado.choices)

    class Meta:
        model = Asignatura
        fields = ['modulo', 'tipo', 'estado']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(descripcion__icontains=value) |
            Q(modulo__nombre__icontains=value)
        )


class CompetenciaFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search', label='Búsqueda'
    )
    asignatura = django_filters.NumberFilter(field_name='asignatura__id')
    tipo = django_filters.ChoiceFilter(choices=Competencia.TipoCompetencia.choices)

    class Meta:
        model = Competencia
        fields = ['asignatura', 'tipo']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(codigo__icontains=value) |
            Q(nombre__icontains=value) |
            Q(descripcion__icontains=value)
        )


class RAPFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search', label='Búsqueda'
    )
    competencia = django_filters.NumberFilter(field_name='competencia__id')

    class Meta:
        model = ResultadoAprendizaje
        fields = ['competencia']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(codigo__icontains=value) |
            Q(descripcion__icontains=value)
        )