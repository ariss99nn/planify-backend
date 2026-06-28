# programa/tests/factories.py
"""
Factories del módulo programa.
Archivo creado desde cero — no existía en el proyecto.

Dependencias de creación:
  make_programa() → independiente
  make_version(programa) → necesita un Programa
  make_modulo(version) → necesita una VersionPrograma
"""
from datetime import date

from programa.models.programa_model import Programa
from programa.models.version_programa_model import VersionPrograma
from programa.models.modulo_model import Modulo


def make_programa(
    nombre=None,
    nivel=Programa.Nivel.TECNICO,
    horas_lectivas=1200,
    horas_practicas=600,
    estado=Programa.Estado.ACTIVO,
    trimestres_totales=6,
    tipo_formacion=Programa.TipoFormacion.POR_OFERTA,
    **kwargs,
):
    """
    Crea un Programa con valores mínimos válidos.
    tipo_formacion=POR_OFERTA es el más simple (no requiere trimestres_cadena).
    """
    counter = Programa.objects.count()
    nombre_final = nombre or f'Programa Test {counter}'
    return Programa.objects.create(
        nombre=nombre_final,
        nivel=nivel,
        horas_lectivas=horas_lectivas,
        horas_practicas=horas_practicas,
        estado=estado,
        trimestres_totales=trimestres_totales,
        tipo_formacion=tipo_formacion,
        **kwargs,
    )


def make_version(
    programa=None,
    numero=None,
    vigente=False,
    fecha_inicio=None,
    **kwargs,
):
    """
    Crea una VersionPrograma.
    Si vigente=True, otras versiones vigentes del mismo programa
    quedan automáticamente en vigente=False (lógica del modelo save()).
    """
    if programa is None:
        programa = make_programa()

    # Generar número único para el programa
    if numero is None:
        existing_nums = list(
            VersionPrograma.objects.filter(programa=programa)
            .values_list('numero', flat=True)
        )
        numero = max(existing_nums, default=0) + 1

    return VersionPrograma.objects.create(
        programa=programa,
        numero=numero,
        vigente=vigente,
        fecha_inicio=fecha_inicio or date(2024, 1, 1),
        **kwargs,
    )


def make_modulo(
    version=None,
    nombre=None,
    orden=None,
    horas_lectivas=80,
    horas_practicas=40,
    estado=Modulo.Estado.ACTIVO,
    **kwargs,
):
    """
    Crea un Módulo dentro de una VersionPrograma.
    El orden es único por versión — se autoincrementa si ya existe.
    """
    if version is None:
        version = make_version()

    if nombre is None:
        counter = Modulo.objects.filter(version=version).count()
        nombre = f'Módulo Test {counter}'

    # Encontrar primer orden disponible
    if orden is None:
        existing_orders = list(
            Modulo.objects.filter(version=version)
            .values_list('orden', flat=True)
        )
        orden = max(existing_orders, default=0) + 1

    return Modulo.objects.create(
        version=version,
        nombre=nombre,
        orden=orden,
        horas_lectivas=horas_lectivas,
        horas_practicas=horas_practicas,
        estado=estado,
        **kwargs,
    )