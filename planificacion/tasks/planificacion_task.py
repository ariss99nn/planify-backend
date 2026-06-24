# planificacion/tasks.py
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def generar_novedades_planificacion():
    """
    Detecta problemas operativos y crea Novedades automáticamente.
    Ejecutar diariamente via Celery Beat.

    CORRECCIÓN: se separaron los dos tipos de novedad en queries
    independientes con criterios de estado coherentes:
    - FICHA_SIN_PLAN  → planes BORRADOR/EN_REVISION con inicio próximo.
    - PLAN_SIN_DOCENTE → planes EN_EJECUCION con ítems sin docente
      (no tiene sentido alertar por docente faltante en un plan no aprobado).
    """
    from django.contrib.contenttypes.models import ContentType

    from ficha.models.ficha_model import Ficha
    from planificacion.models.item_plan_model import ItemPlan
    from planificacion.selectors.planificacion_selector import (
        get_items_sin_docente,
        get_planes_en_ejecucion_con_items_sin_docente,
        get_planes_sin_aprobar_proximos,
    )
    from reportes.models.novedad_model import Novedad

    creadas = 0

    # ------------------------------------------------------------------
    # 1. Planes próximos sin aprobar
    # ------------------------------------------------------------------
    for plan in get_planes_sin_aprobar_proximos(dias=5):
        ya_existe = Novedad.objects.filter(
            tipo=Novedad.Tipo.FICHA_SIN_PLAN,
            object_id=plan.ficha.pk,
            atendida=False,
        ).exists()
        if not ya_existe:
            Novedad.objects.create(
                tipo=Novedad.Tipo.FICHA_SIN_PLAN,
                prioridad=1,
                titulo=f'Plan sin aprobar — Ficha {plan.ficha.codigo_ficha}',
                descripcion=(
                    f'El plan del trimestre {plan.trimestre} de la ficha '
                    f'{plan.ficha.codigo_ficha} ({plan.ficha.version.programa.nombre}) '
                    f'aún no está aprobado y el trimestre inicia el {plan.fecha_inicio}.'
                ),
                content_type=ContentType.objects.get_for_model(Ficha),
                object_id=plan.ficha.pk,
                generada_por_sistema=True,
            )
            creadas += 1

    # ------------------------------------------------------------------
    # 2. Ítems sin docente en planes ya en ejecución
    # ------------------------------------------------------------------
    for plan in get_planes_en_ejecucion_con_items_sin_docente():
        for item in get_items_sin_docente(plan):
            ya_existe = Novedad.objects.filter(
                tipo=Novedad.Tipo.PLAN_SIN_DOCENTE,
                object_id=item.pk,
                atendida=False,
            ).exists()
            if not ya_existe:
                Novedad.objects.create(
                    tipo=Novedad.Tipo.PLAN_SIN_DOCENTE,
                    prioridad=1,
                    titulo=f'Competencia sin docente — {item.competencia.codigo}',
                    descripcion=(
                        f'La competencia {item.competencia.nombre} en el plan '
                        f'trimestre {plan.trimestre} de la ficha '
                        f'{plan.ficha.codigo_ficha} no tiene docente asignado.'
                    ),
                    content_type=ContentType.objects.get_for_model(ItemPlan),
                    object_id=item.pk,
                    generada_por_sistema=True,
                )
                creadas += 1

    logger.info("Novedades de planificación generadas: %d", creadas)
    return creadas