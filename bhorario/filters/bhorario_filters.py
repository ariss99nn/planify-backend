# bhorario/filters/bhorario_filters.py
import django_filters
from django.db.models import Q
from bhorario.models.bloque_horario_model import BloqueHorario

class BloqueHorarioFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search', label='Búsqueda'
    )
    dia_semana = django_filters.ChoiceFilter(
        choices=BloqueHorario.DiaSemana.choices
    )
    jornada = django_filters.ChoiceFilter(
        choices=BloqueHorario.Jornada.choices
    )
    docente = django_filters.NumberFilter(field_name='docente__id')
    aula = django_filters.NumberFilter(field_name='aula__id')
    ficha = django_filters.NumberFilter(field_name='ficha__id')
    hora_inicio = django_filters.TimeFilter(
        field_name='hora_inicio', lookup_expr='gte', label='Desde'
    )
    hora_fin = django_filters.TimeFilter(
        field_name='hora_fin', lookup_expr='lte', label='Hasta'
    )

    class Meta:
        model = BloqueHorario
        fields = ['dia_semana', 'jornada', 'docente', 'aula', 'ficha']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(aula__codigo_aula__icontains=value) |
            Q(docente__user__nombre__icontains=value) |
            Q(ficha__codigo_ficha__icontains=value)
        )