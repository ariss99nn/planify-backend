from programa.models.programa_model import Programa
from programa.models.version_programa_model import VersionPrograma
from programa.models.modulo_model import Modulo
from programa.models.docente_modulo_model import DocenteModulo
from datetime import date


def make_programa(
    nombre='Técnico en Sistemas',
    nivel=Programa.Nivel.TECNICO,
    estado=Programa.Estado.ACTIVO,
    horas_lectivas=1200,
    horas_practicas=600,
    **kwargs,
):
    counter = Programa.objects.count()
    return Programa.objects.create(
        nombre=nombre if not counter else f'{nombre} {counter}',
        nivel=nivel,
        estado=estado,
        horas_lectivas=horas_lectivas,
        horas_practicas=horas_practicas,
        **kwargs,
    )


def make_version(
    programa=None,
    numero=1,
    vigente=True,
    fecha_inicio=None,
    **kwargs,
):
    if programa is None:
        programa = make_programa()
    if fecha_inicio is None:
        fecha_inicio = date(2024, 1, 1)
    # Evitar conflicto de unique_together
    numero_final = numero
    while VersionPrograma.objects.filter(
        programa=programa, numero=numero_final
    ).exists():
        numero_final += 1
    return VersionPrograma.objects.create(
        programa=programa,
        numero=numero_final,
        vigente=vigente,
        fecha_inicio=fecha_inicio,
        **kwargs,
    )


def make_modulo(
    version=None,
    nombre='Fundamentos de Programación',
    orden=1,
    horas_lectivas=80,
    horas_practicas=40,
    estado=Modulo.Estado.ACTIVO,
    **kwargs,
):
    if version is None:
        version = make_version()
    # Evitar conflicto de unique_together
    orden_final = orden
    while Modulo.objects.filter(
        version=version, orden=orden_final
    ).exists():
        orden_final += 1
    return Modulo.objects.create(
        version=version,
        nombre=nombre,
        orden=orden_final,
        horas_lectivas=horas_lectivas,
        horas_practicas=horas_practicas,
        estado=estado,
        **kwargs,
    )


def make_docente_modulo(docente, modulo=None, activo=True):
    if modulo is None:
        modulo = make_modulo()
    return DocenteModulo.objects.create(
        docente=docente,
        modulo=modulo,
        activo=activo,
    )

def make_ficha_para_estudiante(version, estudiante):
    from ficha.models.ficha_model import Ficha
    from ficha.models.ficha_estudiante_model import FichaEstudiante
    from datetime import date
    counter = Ficha.objects.count()
    ficha = Ficha.objects.create(
        codigo_ficha=f'FICHA-{counter:04d}',
        version=version,
        jornada=Ficha.Jornada.MANANA,
        numero_estudiantes_estimado=30,
        etapa=Ficha.Etapa.LECTIVA,
        horas_semanales_objetivo=40,
        trimestre=1,
        estado=True,
        fecha_inicio=date(2024, 1, 1),
    )
    FichaEstudiante.objects.create(
        ficha=ficha,
        estudiante=estudiante,
        activo=True,
        es_cadena=False,
    )
    return ficha