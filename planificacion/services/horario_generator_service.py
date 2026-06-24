# planificacion/services/horario_generator_service.py
import logging
from datetime import time
from decimal import Decimal

from django.db import transaction

from bhorario.models.bloque_horario_model import BloqueHorario
from bhorario.services.bloque_service import BloqueHorarioService, ColisionError

logger = logging.getLogger(__name__)

SLOTS_POR_JORNADA = {
    BloqueHorario.Jornada.MANANA: [
        (time(6,  0), time(8,  0)),
        (time(8,  0), time(10, 0)),
        (time(10, 0), time(12, 0)),
    ],
    BloqueHorario.Jornada.TARDE: [
        (time(12, 0), time(14, 0)),
        (time(14, 0), time(16, 0)),
        (time(16, 0), time(18, 0)),
    ],
    BloqueHorario.Jornada.NOCHE: [
        (time(18, 0), time(20, 0)),
        (time(20, 0), time(22, 0)),
    ],
}

DIAS_HABILES = [
    BloqueHorario.DiaSemana.LUNES,
    BloqueHorario.DiaSemana.MARTES,
    BloqueHorario.DiaSemana.MIERCOLES,
    BloqueHorario.DiaSemana.JUEVES,
    BloqueHorario.DiaSemana.VIERNES,
]


def _calcular_horas(h_inicio: time, h_fin: time) -> Decimal:
    """
    Calcula la duración real en horas entre dos TimeField.
    Bug #3 RESUELTO: elimina el hardcode de horas_ejecutadas=2.
    """
    minutos = (h_fin.hour * 60 + h_fin.minute) - (h_inicio.hour * 60 + h_inicio.minute)
    return Decimal(str(round(minutos / 60, 1)))


class HorarioGeneratorService:
    """
    Genera bloques horarios automáticamente desde un PlanTrimestral aprobado.

    CORRECCIONES aplicadas:
    - Bug #2: ahora busca y asigna un Aula activa disponible en cada slot.
    - Bug #3: horas_ejecutadas se calcula desde la duración real del slot,
      no está hardcodeado a 2.
    - Bug #7: guard de idempotencia al inicio de generar() — lanza ValueError
      si ya existen bloques para la ficha del plan.

    Algoritmo:
    1. Verifica idempotencia (no regenera si ya hay bloques).
    2. Ordena ítems: PRINCIPAL primero, TRANSVERSAL al final.
    3. Omite ítems sin docente asignado (los registra como conflicto).
    4. Para cada ítem itera días × slots buscando:
       a. Docente disponible (bloques existentes + restricciones de Disponibilidad).
       b. Ficha disponible.
       c. Aula activa disponible en la jornada.
    5. Crea el bloque con aula asignada y BloqueCompetencia con horas reales.
    6. Si no hay slot o no hay aula: registra el conflicto sin abortar.
    """

    def __init__(self, plan, dias=None):
        from planificacion.models.plan_trimestral_model import PlanTrimestral

        if plan.estado != PlanTrimestral.EstadoPlan.APROBADO:
            raise ValueError('El plan debe estar aprobado antes de generar horarios.')

        self.plan            = plan
        self.jornada         = plan.ficha.jornada
        self.dias            = dias or DIAS_HABILES
        self.slots           = SLOTS_POR_JORNADA.get(self.jornada, [])
        self.bloques_creados = []
        self.conflictos      = []

    def _buscar_aula_disponible(self, dia: str, h_inicio: time, h_fin: time):
        """
        Busca la primera Aula activa con la jornada correcta
        que no tenga ningún BloqueHorario en el slot pedido.

        Bug #2 RESUELTO: el generador original no asignaba aula,
        creando bloques con aula=null.
        """
        from aulas.models.aula_model import Aula

        ocupadas = list(
            BloqueHorario.objects.filter(
                dia_semana=dia,
                hora_inicio__lt=h_fin,
                hora_fin__gt=h_inicio,
                aula__isnull=False,
            ).values_list('aula_id', flat=True)
        )

        return (
            Aula.objects
            .filter(estado=Aula.Estado.ACTIVA, jornada=self.jornada)
            .exclude(pk__in=ocupadas)
            .first()
        )

    @transaction.atomic
    def generar(self) -> dict:
        """
        Genera los BloqueHorario y BloqueCompetencia para el plan.

        Retorna:
            {
                'bloques_creados': int,
                'conflictos': list[dict],
                'completado': bool,
            }
        """
        from planificacion.models.bloque_competencia_model import BloqueCompetencia

        # ── Bug #7 RESUELTO: guard de idempotencia ────────────────────────
        existentes = BloqueHorario.objects.filter(
            ficha=self.plan.ficha
        ).count()
        if existentes > 0:
            raise ValueError(
                f'Ya existen {existentes} bloques para la ficha '
                f'"{self.plan.ficha}". '
                'Use el endpoint /regenerar-horario/ para borrar y regenerar.'
            )

        items = self.plan.items.select_related(
            'competencia', 'docente'
        ).order_by('competencia__tipo', 'orden')

        for item in items:
            # Omitir ítems sin docente — no se puede generar horario
            if not item.docente_id:
                self.conflictos.append({
                    'item':  str(item),
                    'dia':   None,
                    'hora':  None,
                    'error': 'El ítem no tiene docente asignado.',
                })
                continue

            horas_restantes = float(item.horas_asignadas)

            for dia in self.dias:
                if horas_restantes <= 0:
                    break

                for h_inicio, h_fin in self.slots:
                    if horas_restantes <= 0:
                        break

                    # ── Verificar disponibilidad (docente + ficha) ────────
                    # verificar_disponibilidad() ahora también consulta
                    # el modelo Disponibilidad gracias al Bug #1 resuelto.
                    disponibilidad = BloqueHorarioService.verificar_disponibilidad(
                        dia=dia,
                        hora_inicio=h_inicio,
                        hora_fin=h_fin,
                        docente=item.docente,
                        ficha=self.plan.ficha,
                    )
                    if not disponibilidad['disponible']:
                        continue

                    # ── Bug #2 RESUELTO: buscar aula disponible ───────────
                    aula = self._buscar_aula_disponible(dia, h_inicio, h_fin)
                    if aula is None:
                        self.conflictos.append({
                            'item':  str(item),
                            'dia':   dia,
                            'hora':  f'{h_inicio}-{h_fin}',
                            'error': 'No hay aula activa disponible en este slot.',
                        })
                        continue

                    # ── Bug #3 RESUELTO: duración real del slot ───────────
                    duracion_horas = _calcular_horas(h_inicio, h_fin)

                    try:
                        bloque = BloqueHorarioService.crear_bloque({
                            'dia_semana':  dia,
                            'hora_inicio': h_inicio,
                            'hora_fin':    h_fin,
                            'jornada':     self.jornada,
                            'docente':     item.docente,
                            'ficha':       self.plan.ficha,
                            'aula':        aula,          # ← Bug #2
                        })
                        BloqueCompetencia.objects.create(
                            bloque=bloque,
                            item_plan=item,
                            horas_ejecutadas=duracion_horas,  # ← Bug #3
                        )
                        self.bloques_creados.append(bloque.pk)
                        horas_restantes -= float(duracion_horas)

                    except ColisionError as e:
                        self.conflictos.append({
                            'item':  str(item),
                            'dia':   dia,
                            'hora':  f'{h_inicio}-{h_fin}',
                            'error': str(e),
                        })

        return {
            'bloques_creados': len(self.bloques_creados),
            'conflictos':      self.conflictos,
            'completado':      len(self.conflictos) == 0,
        }