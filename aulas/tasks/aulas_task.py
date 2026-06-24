from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def detectar_aulas_con_conflicto():
    """
    Detecta aulas en mantenimiento que tienen BloqueHorario activos asignados
    y genera una Novedad por cada una que aún no esté reportada.
    """
    from aulas.models.aula_model import Aula
    from bhorario.models.bloque_horario_model import BloqueHorario
    from reportes.models.novedad_model import Novedad
    from django.contrib.contenttypes.models import ContentType

    aulas_problema = Aula.objects.filter(
        estado=Aula.Estado.MANTENIMIENTO,
        bloques_horario__isnull=False,
    ).distinct()

    creadas = 0
    ct_aula = ContentType.objects.get_for_model(Aula)

    for aula in aulas_problema:
        ya_existe = Novedad.objects.filter(
            tipo=Novedad.Tipo.AULA_CONFLICTO,
            content_type=ct_aula,
            object_id=aula.pk,
            atendida=False,
        ).exists()
        if ya_existe:
            continue

        n_bloques = BloqueHorario.objects.filter(aula=aula).count()
        Novedad.objects.create(
            tipo=Novedad.Tipo.AULA_CONFLICTO,
            prioridad=1,
            titulo=f'Aula en mantenimiento con bloques — {aula.codigo_aula}',
            descripcion=(
                f'El aula {aula.codigo_aula} está en mantenimiento '
                f'pero tiene {n_bloques} bloque(s) de horario asignados.'
            ),
            content_type=ct_aula,
            object_id=aula.pk,
            generada_por_sistema=True,
        )
        creadas += 1

    logger.info("Novedades de aulas generadas: %d", creadas)
    return creadas