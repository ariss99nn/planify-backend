# competencia/tests/factories.py
"""
Factories del módulo competencia.
Archivo creado desde cero — no existía en el proyecto.

Importante:
- Competencia PRINCIPAL requiere asignatura (no puede ser null).
- Competencia TRANSVERSAL requiere asignatura=None y horas_trimestre_transversal.
- La función make_competencia() crea PRINCIPAL por defecto.
- Para transversales usar make_competencia_transversal().
"""
from competencia.models.asignatura_model import Asignatura
from competencia.models.competencia_model import Competencia
from competencia.models.resultado_aprendizaje_model import ResultadoAprendizaje
from programa.tests.factories import make_modulo


def make_asignatura(
    modulo=None,
    nombre=None,
    tipo=Asignatura.Tipo.TEORICO_PRACTICA,
    horas_lectivas=80,
    horas_practicas=40,
    orden=None,
    estado=Asignatura.Estado.ACTIVA,
    **kwargs,
):
    """
    Crea una Asignatura dentro de un Módulo.
    El orden es único por módulo — se autoincrementa.
    """
    if modulo is None:
        modulo = make_modulo()

    if nombre is None:
        counter = Asignatura.objects.filter(modulo=modulo).count()
        nombre = f'Asignatura Test {counter}'

    if orden is None:
        existing_orders = list(
            Asignatura.objects.filter(modulo=modulo)
            .values_list('orden', flat=True)
        )
        orden = max(existing_orders, default=0) + 1

    return Asignatura.objects.create(
        modulo=modulo,
        nombre=nombre,
        tipo=tipo,
        horas_lectivas=horas_lectivas,
        horas_practicas=horas_practicas,
        orden=orden,
        estado=estado,
        **kwargs,
    )


def make_competencia(
    asignatura=None,
    codigo=None,
    nombre=None,
    tipo=Competencia.TipoCompetencia.PRINCIPAL,
    **kwargs,
):
    """
    Crea una Competencia PRINCIPAL.

    IMPORTANTE: Competencia PRINCIPAL requiere asignatura (clean() lo valida).
    Si no se pasa, se crea una automáticamente.

    Para transversales usar make_competencia_transversal().
    """
    if asignatura is None:
        asignatura = make_asignatura()

    counter = Competencia.objects.count()
    codigo_final = codigo or f'COMP-{counter:04d}'
    # Evitar código duplicado (campo unique)
    while Competencia.objects.filter(codigo=codigo_final).exists():
        counter += 1
        codigo_final = f'COMP-{counter:04d}'

    nombre_final = nombre or f'Competencia Test {counter}'

    return Competencia.objects.create(
        asignatura=asignatura,
        tipo=tipo,
        codigo=codigo_final,
        nombre=nombre_final,
        **kwargs,
    )


def make_competencia_transversal(
    codigo=None,
    nombre=None,
    horas_trimestre_transversal=4,
    es_induccion=False,
    **kwargs,
):
    """
    Crea una Competencia TRANSVERSAL.

    IMPORTANTE: asignatura DEBE ser None (clean() lo valida).
    horas_trimestre_transversal es obligatorio para transversales.
    """
    counter = Competencia.objects.count()
    codigo_final = codigo or f'TRANS-{counter:04d}'
    while Competencia.objects.filter(codigo=codigo_final).exists():
        counter += 1
        codigo_final = f'TRANS-{counter:04d}'

    return Competencia.objects.create(
        asignatura=None,
        tipo=Competencia.TipoCompetencia.TRANSVERSAL,
        codigo=codigo_final,
        nombre=nombre or f'Competencia Transversal Test {counter}',
        horas_trimestre_transversal=horas_trimestre_transversal,
        es_induccion=es_induccion,
        **kwargs,
    )


def make_rap(
    competencia=None,
    codigo=None,
    descripcion=None,
    **kwargs,
):
    """Crea un ResultadoAprendizaje."""
    if competencia is None:
        competencia = make_competencia()

    counter = ResultadoAprendizaje.objects.count()
    codigo_final = codigo or f'RAP-{counter:04d}'
    while ResultadoAprendizaje.objects.filter(codigo=codigo_final).exists():
        counter += 1
        codigo_final = f'RAP-{counter:04d}'

    return ResultadoAprendizaje.objects.create(
        competencia=competencia,
        codigo=codigo_final,
        descripcion=descripcion or f'Resultado de aprendizaje test {counter}.',
        **kwargs,
    )