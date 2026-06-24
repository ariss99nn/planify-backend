from aulas.models.bloque_model import Bloque
from aulas.models.equipamiento_model import Equipamiento
from aulas.models.aula_model import Aula


def make_bloque(nombre='Bloque A', pisos=3, capacidad_maxima=200, **kwargs):
    counter = Bloque.objects.count()
    return Bloque.objects.create(
        nombre=nombre if not counter else f'{nombre} {counter}',
        pisos=pisos,
        capacidad_maxima=capacidad_maxima,
        **kwargs,
    )


def make_equipamiento(
    nombre='Proyector',
    cantidad=1,
    estado=Equipamiento.Estado.FUNCIONAL,
    **kwargs,
):
    counter = Equipamiento.objects.count()
    return Equipamiento.objects.create(
        nombre=nombre if not counter else f'{nombre} {counter}',
        cantidad=cantidad,
        estado=estado,
        **kwargs,
    )


def make_aula(
    bloque=None,
    codigo='A101',
    capacidad=30,
    tipo=Aula.TipoAula.TEORICA,
    estado=Aula.Estado.ACTIVA,
    **kwargs,
):
    if bloque is None:
        bloque = make_bloque()
    counter = Aula.objects.count()
    return Aula.objects.create(
        codigo_aula=codigo if not counter else f'{codigo}{counter}',
        capacidad=capacidad,
        tipo_aula=tipo,
        estado=estado,
        bloque=bloque,
        **kwargs,
    )