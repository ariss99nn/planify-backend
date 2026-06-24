import logging
from celery import shared_task
from django.db.models import Sum, ExpressionWrapper, F, IntegerField, Q
from django.db.models.functions import ExtractHour, ExtractMinute

logger = logging.getLogger(__name__)


def _contar_docentes_sobrecargados(docentes_qs) -> int:

    from bhorario.models.bloque_horario_model import BloqueHorario

    docentes_con_horas = docentes_qs.annotate(
        minutos_asignados=Sum(
            ExpressionWrapper(
                (ExtractHour(F('bloques_horario__hora_fin')) * 60
                 + ExtractMinute(F('bloques_horario__hora_fin')))
                - (ExtractHour(F('bloques_horario__hora_inicio')) * 60
                   + ExtractMinute(F('bloques_horario__hora_inicio'))),
                output_field=IntegerField(),
            ),
            filter=Q(bloques_horario__es_recurrente=True),
        )
    )

    sobrecargados = 0
    for docente in docentes_con_horas:
        minutos = docente.minutos_asignados or 0
        horas   = round(minutos / 60, 1)
        if horas > docente.horas_max_efectivas:
            sobrecargados += 1

    return sobrecargados


@shared_task
def generar_snapshot_diario():
    """Genera el snapshot de analítica del día. Ejecutar via Celery Beat."""
    from django.utils import timezone
    from django.db.models import Sum

    from analitica.models.analitica_snapshot_model import AnaliticaSnapshot
    from analitica.models.snapshot_programa_model import SnapshotPrograma
    from ficha.models.ficha_model import Ficha
    from ficha.models.ficha_estudiante_model import FichaEstudiante
    from docentes.models.docente_model import Docente
    from aulas.models.aula_model import Aula
    from planificacion.models.plan_trimestral_model import PlanTrimestral
    from planificacion.models.item_plan_model import ItemPlan
    from alertas.models.alerta_model import Alerta
    from programa.models.programa_model import Programa
    from bhorario.models.bloque_horario_model import BloqueHorario

    hoy        = timezone.now().date()
    mes_actual = hoy.replace(day=1)

    if AnaliticaSnapshot.objects.filter(fecha=hoy).exists():
        logger.warning('Snapshot del %s ya existe — tarea omitida.', hoy)
        return None

    fichas_activas    = Ficha.objects.filter(estado=Ficha.Estado.ACTIVA)
    docentes_activos  = Docente.objects.filter(estado=True)
    total_docentes    = docentes_activos.count()

    sobrecargados = _contar_docentes_sobrecargados(docentes_activos)

    snapshot = AnaliticaSnapshot.objects.create(
        fecha=hoy,
        fichas_activas=fichas_activas.count(),
        fichas_lectiva=fichas_activas.filter(etapa=Ficha.Etapa.LECTIVA).count(),
        fichas_productiva=fichas_activas.filter(etapa=Ficha.Etapa.PRODUCTIVA).count(),
        estudiantes_activos=FichaEstudiante.objects.filter(activo=True).count(),
        deserciones_mes=FichaEstudiante.objects.filter(
            activo=False,
            motivo_retiro=FichaEstudiante.MotivoRetiro.DESERCION,
            fecha_retiro__gte=mes_actual,
        ).count(),
        graduados_mes=FichaEstudiante.objects.filter(
            activo=False,
            motivo_retiro=FichaEstudiante.MotivoRetiro.GRADUADO,
            fecha_retiro__gte=mes_actual,
        ).count(),
        reasignaciones_mes=FichaEstudiante.objects.filter(
            activo=False,
            motivo_retiro=FichaEstudiante.MotivoRetiro.REASIGNADO,
            fecha_retiro__gte=mes_actual,
        ).count(),
        docentes_activos=total_docentes,
        docentes_sobrecargados=sobrecargados,
        aulas_activas=Aula.objects.filter(estado=Aula.Estado.ACTIVA).count(),
        aulas_mantenimiento=Aula.objects.filter(estado=Aula.Estado.MANTENIMIENTO).count(),
        aulas_inactivas=Aula.objects.filter(estado=Aula.Estado.INACTIVA).count(),
        planes_aprobados=PlanTrimestral.objects.filter(
            estado__in=[
                PlanTrimestral.EstadoPlan.APROBADO,
                PlanTrimestral.EstadoPlan.EN_EJECUCION,
            ]
        ).count(),
        planes_pendientes=PlanTrimestral.objects.filter(
            estado__in=[
                PlanTrimestral.EstadoPlan.BORRADOR,
                PlanTrimestral.EstadoPlan.EN_REVISION,
            ]
        ).count(),
        alertas_pendientes=Alerta.objects.filter(
            estado=Alerta.EstadoAlerta.PENDIENTE,
        ).count(),
        conflictos_horario_mes=Alerta.objects.filter(
            tipo=Alerta.TipoAlerta.CONFLICTO,
            fecha_creacion__date__gte=mes_actual,
        ).count(),
    )

    snapshot_programas = []

    for programa in Programa.objects.filter(estado=Programa.Estado.ACTIVO):
        fichas_prog = fichas_activas.filter(version__programa=programa)

        estudiantes_prog = FichaEstudiante.objects.filter(
            ficha__in=fichas_prog, activo=True
        ).count()
        deserciones_prog = FichaEstudiante.objects.filter(
            ficha__in=fichas_prog,
            activo=False,
            motivo_retiro=FichaEstudiante.MotivoRetiro.DESERCION,
            fecha_retiro__gte=mes_actual,
        ).count()
        graduados_prog = FichaEstudiante.objects.filter(
            ficha__in=fichas_prog,
            activo=False,
            motivo_retiro=FichaEstudiante.MotivoRetiro.GRADUADO,
            fecha_retiro__gte=mes_actual,
        ).count()

        horas_plan = (
            ItemPlan.objects
            .filter(plan__ficha__in=fichas_prog)
            .aggregate(total=Sum('horas_asignadas'))['total'] or 0
        )

        bloques = BloqueHorario.objects.filter(
            ficha__in=fichas_prog,
        ).values_list('hora_inicio', 'hora_fin')

        horas_ej = sum(
            (fin.hour * 60 + fin.minute - inicio.hour * 60 - inicio.minute) / 60
            for inicio, fin in bloques
            if fin > inicio
        )

        snapshot_programas.append(SnapshotPrograma(
            snapshot=snapshot,
            programa=programa,
            fichas_activas=fichas_prog.count(),
            fichas_lectiva=fichas_prog.filter(etapa=Ficha.Etapa.LECTIVA).count(),
            fichas_productiva=fichas_prog.filter(etapa=Ficha.Etapa.PRODUCTIVA).count(),
            estudiantes_activos=estudiantes_prog,
            deserciones_mes=deserciones_prog,
            graduados_mes=graduados_prog,
            horas_planificadas=horas_plan,
            horas_ejecutadas=round(horas_ej),
            avance_curricular_pct=0,
        ))

    SnapshotPrograma.objects.bulk_create(snapshot_programas)

    logger.info(
        'Snapshot generado: %s — %d programas procesados.',
        hoy,
        len(snapshot_programas),
    )
    return snapshot.pk