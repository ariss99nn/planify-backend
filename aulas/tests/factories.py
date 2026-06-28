# aulas/tests/factories.py
"""
Factories del módulo aulas.

CORRECCIÓN CRÍTICA aplicada:
- make_aula() no pasaba el campo `piso` → IntegrityError en BD.
  El campo Aula.piso es PositiveIntegerField sin default y sin null=True.
  Se añade piso=1 como valor por defecto seguro (bloque tiene pisos=3).

- Aula.Estado valores cortos: 'ACT', 'MANT', 'INAC' (no 'ACTIVA', etc.)
- Aula.TipoAula valores cortos: 'LAB', 'TEO', 'SIS', 'OTR'
"""
from aulas.models.bloque_model import Bloque
from aulas.models.equipamiento_model import Equipamiento
from aulas.models.aula_model import Aula


def make_bloque(nombre=None, pisos=3, capacidad_maxima=200, **kwargs):
    counter = Bloque.objects.count()
    nombre_final = nombre or f'Bloque Test {counter}'
    while Bloque.objects.filter(nombre=nombre_final).exists():
        counter += 1
        nombre_final = nombre or f'Bloque Test {counter}'
    return Bloque.objects.create(
        nombre=nombre_final,
        pisos=pisos,
        capacidad_maxima=capacidad_maxima,
        **kwargs,
    )


def make_equipamiento(nombre=None, cantidad=1, estado=None, **kwargs):
    if estado is None:
        estado = Equipamiento.Estado.FUNCIONAL
    counter = Equipamiento.objects.count()
    nombre_final = nombre or f'Equipo Test {counter}'
    return Equipamiento.objects.create(
        nombre=nombre_final,
        cantidad=cantidad,
        estado=estado,
        **kwargs,
    )


def make_aula(
    bloque=None,
    codigo=None,
    capacidad=30,
    tipo=None,
    estado=None,
    piso=1,         # CORRECCIÓN: campo requerido que faltaba
    **kwargs,
):
    """
    CORRECCIÓN: Aula.piso es campo requerido (no nullable, sin default).
    La versión anterior no lo pasaba → IntegrityError en BD.

    piso=1 es seguro ya que make_bloque() crea bloques con pisos=3 por defecto.
    """
    if bloque is None:
        bloque = make_bloque()
    if tipo is None:
        tipo = Aula.TipoAula.TEORICA   # valor: 'TEO'
    if estado is None:
        estado = Aula.Estado.ACTIVA    # valor: 'ACT'

    # Asegurar que piso no supera los pisos del bloque
    if piso > bloque.pisos:
        piso = 1

    counter = Aula.objects.count()
    codigo_final = codigo or f'TEST-{counter:04d}'
    while Aula.objects.filter(codigo_aula=codigo_final).exists():
        counter += 1
        codigo_final = codigo or f'TEST-{counter:04d}'

    return Aula.objects.create(
        codigo_aula=codigo_final,
        capacidad=capacidad,
        tipo_aula=tipo,
        estado=estado,
        bloque=bloque,
        piso=piso,
        **kwargs,
    )