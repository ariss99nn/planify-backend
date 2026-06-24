from datetime import date
from ficha.models.ficha_model import Ficha
from ficha.models.ficha_estudiante_model import FichaEstudiante
from ficha.models.ficha_historial_etapa_model import HistorialEtapa
from ficha.models.ficha_reasignacion_model import ReasignacionFicha
from programa.tests.factories import make_version


def make_ficha(
    version=None,
    codigo=None,
    jornada=Ficha.Jornada.MANANA,
    etapa=Ficha.Etapa.LECTIVA,
    estado=True,
    horas_semanales_objetivo=40,
    trimestre=1,
    numero_estudiantes_estimado=30,
    jefe_grupo=None,
    **kwargs,
):
    if version is None:
        version = make_version()
    counter = Ficha.objects.count()
    codigo_final = codigo or f'FICHA-{counter:04d}'
    while Ficha.objects.filter(codigo_ficha=codigo_final).exists():
        counter += 1
        codigo_final = f'FICHA-{counter:04d}'
    return Ficha.objects.create(
        codigo_ficha=codigo_final,
        version=version,
        jornada=jornada,
        etapa=etapa,
        estado=estado,
        horas_semanales_objetivo=horas_semanales_objetivo,
        trimestre=trimestre,
        numero_estudiantes_estimado=numero_estudiantes_estimado,
        jefe_grupo=jefe_grupo,
        fecha_inicio=date(2024, 1, 1),
        **kwargs,
    )


def make_ficha_estudiante(
    ficha=None,
    estudiante=None,
    activo=True,
    es_cadena=False,
):
    if ficha is None:
        ficha = make_ficha()
    return FichaEstudiante.objects.create(
        ficha=ficha,
        estudiante=estudiante,
        activo=activo,
        es_cadena=es_cadena,
    )


def make_reasignacion(
    estudiante,
    ficha_origen,
    ficha_destino,
    realizado_por=None,
    motivo='Cambio de jornada',
):
    return ReasignacionFicha.objects.create(
        estudiante=estudiante,
        ficha_origen=ficha_origen,
        ficha_destino=ficha_destino,
        motivo=motivo,
        realizado_por=realizado_por,
    )