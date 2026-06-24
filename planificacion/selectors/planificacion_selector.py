# planificacion/selectors/planificacion_selector.py
from planificacion.models.item_plan_model import ItemPlan
from planificacion.models.plan_trimestral_model import PlanTrimestral


def get_carga_docente_trimestre(docente, trimestre):
    """Items activos de un docente en un trimestre dado."""
    return ItemPlan.objects.filter(
        docente=docente,
        plan__trimestre=trimestre,
        plan__estado__in=[
            PlanTrimestral.EstadoPlan.APROBADO,
            PlanTrimestral.EstadoPlan.EN_EJECUCION,
        ],
    ).select_related('competencia', 'plan__ficha')


def get_planes_sin_aprobar_proximos(dias=5):
    """
    Planes en borrador o revisión cuyo inicio está entre hoy y los
    próximos `dias` días — se excluyen planes cuya fecha ya pasó.
    """
    from datetime import timedelta

    from django.utils import timezone

    hoy    = timezone.now().date()
    limite = hoy + timedelta(days=dias)

    return PlanTrimestral.objects.filter(
        estado__in=[
            PlanTrimestral.EstadoPlan.BORRADOR,
            PlanTrimestral.EstadoPlan.EN_REVISION,
        ],
        fecha_inicio__gte=hoy,     # CORRECCIÓN: no incluir planes ya vencidos
        fecha_inicio__lte=limite,
    ).select_related('ficha__version__programa')


def get_items_sin_docente(plan):
    """Items del plan que aún no tienen docente asignado."""
    return plan.items.filter(docente__isnull=True)


def get_planes_en_ejecucion_con_items_sin_docente():
    """
    Planes en ejecución que tienen al menos un ítem sin docente.
    Usado por la tarea Celery para novedades operativas.
    """
    return PlanTrimestral.objects.filter(
        estado=PlanTrimestral.EstadoPlan.EN_EJECUCION,
        items__docente__isnull=True,
    ).distinct().select_related('ficha__version__programa')