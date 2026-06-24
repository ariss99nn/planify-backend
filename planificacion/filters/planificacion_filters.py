# planificacion/filters/planificacion_filters.py
import django_filters

from planificacion.models.item_plan_model import ItemPlan
from planificacion.models.plan_trimestral_model import PlanTrimestral


class PlanTrimestralFilter(django_filters.FilterSet):
    """
    Filtros disponibles:
      ?ficha=<id>
      ?trimestre=<n>
      ?estado=BORRADOR|EN_REVISION|APROBADO|EN_EJECUCION|CERRADO|RECHAZADO
      ?programa=<id>

    CORRECCIÓN: el campo `aprobado` no existe en el modelo — se eliminó.
    Se usa `estado` (CharFilter exact) que cubre todos los estados del flujo.
    Se añade `programa` a Meta.fields para que el filtro tenga efecto.
    """
    ficha     = django_filters.NumberFilter(field_name='ficha__id')
    trimestre = django_filters.NumberFilter(field_name='trimestre')
    estado    = django_filters.CharFilter(field_name='estado', lookup_expr='exact')
    programa  = django_filters.NumberFilter(
        field_name='ficha__version__programa__id'
    )

    class Meta:
        model  = PlanTrimestral
        fields = ['ficha', 'trimestre', 'estado', 'programa']


class ItemPlanFilter(django_filters.FilterSet):
    """
    Filtros disponibles:
      ?plan=<id>
      ?docente=<id>
      ?completado=true|false
      ?tipo_competencia=<valor>
    """
    plan             = django_filters.NumberFilter(field_name='plan__id')
    docente          = django_filters.NumberFilter(field_name='docente__id')
    completado       = django_filters.BooleanFilter(field_name='completado')
    tipo_competencia = django_filters.CharFilter(
        field_name='competencia__tipo', lookup_expr='exact'
    )

    class Meta:
        model  = ItemPlan
        fields = ['plan', 'docente', 'completado', 'tipo_competencia']