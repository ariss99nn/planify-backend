from datetime import time
from bhorario.models.bloque_horario_model import BloqueHorario


# Slots disponibles por jornada para generar bloques sin colisiones
_SLOTS_MANANA = [
    (time(6,  0), time(8,  0)),
    (time(8,  0), time(10, 0)),
    (time(10, 0), time(12, 0)),
]
_SLOTS_TARDE = [
    (time(12, 0), time(14, 0)),
    (time(14, 0), time(16, 0)),
    (time(16, 0), time(18, 0)),
]
_SLOTS_NOCHE = [
    (time(18, 0), time(20, 0)),
    (time(20, 0), time(22, 0)),
]


def make_bloque(
    dia=BloqueHorario.DiaSemana.LUNES,
    hora_inicio=None,
    hora_fin=None,
    jornada=BloqueHorario.Jornada.MANANA,
    aula=None,
    docente=None,
    ficha=None,
):
    """
    CORRECCIÓN: la versión original calculaba hora como 6+counter y 8+counter,
    lo que podía generar time(24,0) o time(25,0) cuando había muchos bloques.
    Ahora rota sobre slots fijos por jornada, evitando horas inválidas.
    Si los 3 slots de la jornada están ocupados para ese docente/ficha/aula,
    cae en el primer slot sin verificar (para tests específicos de colisión).
    """
    if hora_inicio and hora_fin:
        return BloqueHorario.objects.create(
            dia_semana=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            jornada=jornada,
            aula=aula,
            docente=docente,
            ficha=ficha,
        )

    # Seleccionar slot libre según la jornada
    slots_map = {
        BloqueHorario.Jornada.MANANA: _SLOTS_MANANA,
        BloqueHorario.Jornada.TARDE:  _SLOTS_TARDE,
        BloqueHorario.Jornada.NOCHE:  _SLOTS_NOCHE,
    }
    slots = slots_map.get(jornada, _SLOTS_MANANA)

    h_inicio, h_fin = slots[0]  # fallback
    for slot_inicio, slot_fin in slots:
        conflict = BloqueHorario.objects.filter(
            dia_semana=dia,
            hora_inicio=slot_inicio,
            hora_fin=slot_fin,
        )
        if docente:
            conflict = conflict.filter(docente=docente)
        if aula:
            conflict = conflict.filter(aula=aula)
        if ficha:
            conflict = conflict.filter(ficha=ficha)
        if not conflict.exists():
            h_inicio, h_fin = slot_inicio, slot_fin
            break

    return BloqueHorario.objects.create(
        dia_semana=dia,
        hora_inicio=h_inicio,
        hora_fin=h_fin,
        jornada=jornada,
        aula=aula,
        docente=docente,
        ficha=ficha,
    )