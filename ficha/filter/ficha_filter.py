# ficha/filter/ficha_filter.py   ← FIX: directorio sin 's' (consistente con pagination y views)
import django_filters
from django.db.models import Q
from ficha.models.ficha_model import Ficha
from ficha.models.ficha_estudiante_model import FichaEstudiante
from ficha.models.ficha_historial_etapa_model import HistorialEtapa
from ficha.models.ficha_reasignacion_model import ReasignacionFicha


class ReasignacionFilter(django_filters.FilterSet):
    estudiante    = django_filters.NumberFilter(field_name='estudiante__id')
    ficha_origen  = django_filters.NumberFilter(field_name='ficha_origen__id')
    ficha_destino = django_filters.NumberFilter(field_name='ficha_destino__id')

    class Meta:
        model  = ReasignacionFicha
        fields = ['estudiante', 'ficha_origen', 'ficha_destino']


class FichaFilter(django_filters.FilterSet):
    search           = django_filters.CharFilter(method='filter_search', label='Búsqueda')
    etapa            = django_filters.ChoiceFilter(choices=Ficha.Etapa.choices)
    jornada          = django_filters.ChoiceFilter(choices=Ficha.Jornada.choices)
    estado           = django_filters.ChoiceFilter(choices=Ficha.Estado.choices)
    cadena_formacion = django_filters.BooleanFilter()
    programa         = django_filters.NumberFilter(field_name='version__programa__id')
    version          = django_filters.NumberFilter(field_name='version__id')
    jefe_grupo       = django_filters.NumberFilter(field_name='jefe_grupo__id')

    class Meta:
        model  = Ficha
        fields = ['etapa', 'jornada', 'estado', 'cadena_formacion']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(codigo_ficha__icontains=value) |
            Q(version__programa__nombre__icontains=value)
        )


class FichaEstudianteFilter(django_filters.FilterSet):
    activo        = django_filters.BooleanFilter()
    es_cadena     = django_filters.BooleanFilter()
    motivo_retiro = django_filters.ChoiceFilter(choices=FichaEstudiante.MotivoRetiro.choices)
    ficha         = django_filters.NumberFilter(field_name='ficha__id')

    class Meta:
        model  = FichaEstudiante
        fields = ['activo', 'es_cadena', 'motivo_retiro']


class HistorialEtapaFilter(django_filters.FilterSet):
    ficha          = django_filters.NumberFilter(field_name='ficha__id')
    etapa_nueva    = django_filters.ChoiceFilter(choices=Ficha.Etapa.choices)
    etapa_anterior = django_filters.ChoiceFilter(choices=Ficha.Etapa.choices)

    class Meta:
        model  = HistorialEtapa
        fields = ['ficha', 'etapa_nueva', 'etapa_anterior']