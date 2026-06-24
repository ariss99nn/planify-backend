# docentes/tasks/docentes_task.py
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def detectar_docentes_sobrecargados():
    """
    Detecta docentes que superan su horas_max_efectivas y crea
    Novedades si no existen ya una pendiente.

    CORRECCIÓN Bug #5:
    - La versión anterior llamaba docente.esta_sobrecargado en un bucle
      Python → 1 query adicional por docente (N+1).
    - Ahora usa get_docentes_con_horas_anotadas() que calcula todo en
      una sola query SQL con SUM + GROUP BY.
    """
    from django.contrib.contenttypes.models import ContentType

    from docentes.models.docente_model import Docente
    from docentes.selectors.docente_selector import (
        esta_sobrecargado_anotado,
        get_docentes_con_horas_anotadas,
        get_horas_anotadas,
    )
    from reportes.models.novedad_model import Novedad

    # Una sola query SQL — no N+1
    docentes = get_docentes_con_horas_anotadas()
    ct       = ContentType.objects.get_for_model(Docente)
    creadas  = 0

    for docente in docentes:
        if not esta_sobrecargado_anotado(docente):
            continue

        ya_existe = Novedad.objects.filter(
            tipo=Novedad.Tipo.DOCENTE_SOBRECARGADO,
            content_type=ct,
            object_id=docente.pk,
            atendida=False,
        ).exists()
        if ya_existe:
            continue

        horas_asignadas = get_horas_anotadas(docente)

        Novedad.objects.create(
            tipo=Novedad.Tipo.DOCENTE_SOBRECARGADO,
            prioridad=1,
            titulo=f'Docente sobrecargado — {docente.nombre_completo}',
            descripcion=(
                f'{docente.nombre_completo} tiene {horas_asignadas}h '
                f'asignadas esta semana, superando su límite de '
                f'{docente.horas_max_efectivas}h.'
            ),
            content_type=ct,
            object_id=docente.pk,
            generada_por_sistema=True,
        )
        creadas += 1

    logger.info('Novedades de sobrecarga generadas: %d', creadas)
    return creadas