from competencia.models.asignatura_model import Asignatura
from competencia.models.competencia_model import Competencia
from competencia.models.resultado_aprendizaje_model import ResultadoAprendizaje
from competencia.models.docente_asignatura_model import DocenteAsignatura
from programa.tests.factories import make_modulo


def make_asignatura(
    modulo=None,
    nombre='Introducción a la Programación',
    tipo=Asignatura.Tipo.TEORICO_PRACTICA,
    estado=Asignatura.Estado.ACTIVA,
    horas_lectivas=60,
    horas_practicas=30,
    orden=1,
    **kwargs,
):
    if modulo is None:
        modulo = make_modulo()
    orden_final = orden
    while Asignatura.objects.filter(
        modulo=modulo, orden=orden_final
    ).exists():
        orden_final += 1
    return Asignatura.objects.create(
        modulo=modulo,
        nombre=nombre,
        tipo=tipo,
        estado=estado,
        horas_lectivas=horas_lectivas,
        horas_practicas=horas_practicas,
        orden=orden_final,
        **kwargs,
    )


def make_competencia(
    asignatura=None,
    codigo=None,
    nombre='Desarrollar soluciones algorítmicas',
    **kwargs,
):
    if asignatura is None:
        asignatura = make_asignatura()
    counter = Competencia.objects.count()
    codigo_final = codigo or f'COMP-{counter:03d}'
    while Competencia.objects.filter(codigo=codigo_final).exists():
        counter += 1
        codigo_final = f'COMP-{counter:03d}'
    return Competencia.objects.create(
        asignatura=asignatura,
        codigo=codigo_final,
        nombre=nombre,
        **kwargs,
    )


def make_rap(
    competencia=None,
    codigo=None,
    descripcion='Implementa algoritmos básicos de ordenamiento.',
    **kwargs,
):
    if competencia is None:
        competencia = make_competencia()
    counter = ResultadoAprendizaje.objects.count()
    codigo_final = codigo or f'RAP-{counter:03d}'
    while ResultadoAprendizaje.objects.filter(codigo=codigo_final).exists():
        counter += 1
        codigo_final = f'RAP-{counter:03d}'
    return ResultadoAprendizaje.objects.create(
        competencia=competencia,
        codigo=codigo_final,
        descripcion=descripcion,
        **kwargs,
    )


def make_docente_asignatura(docente, asignatura=None, activo=True):
    if asignatura is None:
        asignatura = make_asignatura()
    return DocenteAsignatura.objects.create(
        docente=docente,
        asignatura=asignatura,
        activo=activo,
    )

def make_ficha_para_modulo(modulo):
    from ficha.models.ficha_model import Ficha
    from datetime import date
    counter = Ficha.objects.count()
    return Ficha.objects.create(
        codigo_ficha=f'FICHA-C-{counter:04d}',
        version=modulo.version,
        jornada=Ficha.Jornada.MANANA,
        numero_estudiantes_estimado=25,
        etapa=Ficha.Etapa.LECTIVA,
        horas_semanales_objetivo=40,
        trimestre=1,
        estado=True,
        fecha_inicio=date(2024, 1, 1),
    )
