from datetime import time
from bhorario.models.bloque_horario_model import BloqueHorario


def make_bloque(
    dia=BloqueHorario.DiaSemana.LUNES,
    hora_inicio=None,
    hora_fin=None,
    jornada=BloqueHorario.Jornada.MANANA,
    aula=None,
    docente=None,
    ficha=None,
):
    counter = BloqueHorario.objects.count()
    h_inicio = hora_inicio or time(6 + counter, 0)
    h_fin = hora_fin or time(8 + counter, 0)
    return BloqueHorario.objects.create(
        dia_semana=dia,
        hora_inicio=h_inicio,
        hora_fin=h_fin,
        jornada=jornada,
        aula=aula,
        docente=docente,
        ficha=ficha,
    )