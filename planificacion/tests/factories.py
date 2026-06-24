from datetime import date
from planificacion.models.plan_trimestral_model import PlanTrimestral
from planificacion.models.item_plan_model import ItemPlan
from planificacion.models.bloque_competencia_model import BloqueCompetencia
from ficha.tests.factories import make_ficha
from competencia.tests.factories import make_competencia
from docentes.tests.factories import make_docente


def make_plan(ficha=None, trimestre=1, aprobado=False, **kwargs):
    if ficha is None:
        ficha = make_ficha()
    counter = PlanTrimestral.objects.filter(ficha=ficha).count()
    trimestre_final = trimestre + counter
    return PlanTrimestral.objects.create(
        ficha=ficha,
        trimestre=trimestre_final,
        fecha_inicio=date(2024, 1, 1),
        fecha_fin=date(2024, 4, 30),
        aprobado=aprobado,
        **kwargs,
    )


def make_item(plan=None, competencia=None, docente=None, horas=20, orden=1):
    if plan is None:
        plan = make_plan()
    if competencia is None:
        competencia = make_competencia()
    counter = ItemPlan.objects.filter(plan=plan).count()
    return ItemPlan.objects.create(
        plan=plan,
        competencia=competencia,
        docente=docente or make_docente(
            user=__import__('users.tests.factories', fromlist=['make_docente']).make_docente(
                email=f'doc_item_{counter}@test.com'
            )
        ),
        horas_asignadas=horas,
        orden=orden + counter,
    )


def make_bloque_competencia(bloque, item_plan, horas=2.0):
    return BloqueCompetencia.objects.create(
        bloque=bloque,
        item_plan=item_plan,
        horas_ejecutadas=horas,
    )