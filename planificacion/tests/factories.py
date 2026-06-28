from datetime import date
from planificacion.models.plan_trimestral_model import PlanTrimestral
from planificacion.models.item_plan_model import ItemPlan
from planificacion.models.bloque_competencia_model import BloqueCompetencia
from ficha.tests.factories import make_ficha
from competencia.tests.factories import make_competencia
from docentes.tests.factories import make_docente   # ← import correcto


def make_plan(ficha=None, trimestre=1, estado=None, **kwargs):
    """
    CORRECCIÓN: PlanTrimestral no tiene campo 'aprobado'.
    El campo correcto es 'estado'. El default es BORRADOR.
    La versión original pasaba aprobado=False/True a objects.create()
    lo que causaba 'unexpected keyword argument aprobado'.
    """
    if ficha is None:
        ficha = make_ficha()

    # Evitar conflicto de unique_together (ficha, trimestre)
    trimestre_final = trimestre
    while PlanTrimestral.objects.filter(
        ficha=ficha, trimestre=trimestre_final
    ).exists():
        trimestre_final += 1

    estado_final = estado or PlanTrimestral.EstadoPlan.BORRADOR

    return PlanTrimestral.objects.create(
        ficha=ficha,
        trimestre=trimestre_final,
        fecha_inicio=date(2024, 1, 1),
        fecha_fin=date(2024, 4, 30),
        estado=estado_final,
        **kwargs,
    )


def make_item(plan=None, competencia=None, docente=None, horas=20, orden=1):
    """
    CORRECCIÓN: la versión original tenía un import anidado roto:
        make_docente(user=__import__('users.tests.factories'...).make_docente(...))
    Esto llamaba make_docente de users (que crea un User) y lo pasaba
    como user= a make_docente de docentes — semánticamente incorrecto
    y causaba DoesNotExist o IntegrityError en BD.
    Ahora importa directamente make_docente de docentes/tests/factories.py.
    """
    if plan is None:
        plan = make_plan()
    if competencia is None:
        competencia = make_competencia()

    # Crear docente único para este ítem si no se provee
    if docente is None:
        counter = ItemPlan.objects.count()
        docente = make_docente(email=f'doc_item_{counter}@test.com')

    # Evitar conflicto de unique_together (plan, orden)
    orden_final = orden
    while ItemPlan.objects.filter(plan=plan, orden=orden_final).exists():
        orden_final += 1

    return ItemPlan.objects.create(
        plan=plan,
        competencia=competencia,
        docente=docente,
        horas_asignadas=horas,
        orden=orden_final,
    )


def make_bloque_competencia(bloque, item_plan, horas=2.0):
    from decimal import Decimal
    return BloqueCompetencia.objects.create(
        bloque=bloque,
        item_plan=item_plan,
        horas_ejecutadas=Decimal(str(horas)),
    )