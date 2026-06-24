# bhorario/services/horario_generator.py
import logging
from django.db import transaction

# FIX S1: import movido al nivel de módulo, fuera del loop
from planificacion.models.bloque_competencia_model import BloqueCompetencia
from bhorario.services.bloque_service import BloqueHorarioService, ColisionError
from bhorario.models.bloque_horario_model import BloqueHorario

logger = logging.getLogger(__name__)


class HorarioGeneratorService:
    """
    Genera automáticamente bloques horarios para una ficha
    basándose en su plan trimestral aprobado.

    Algoritmo:
    1. Obtiene los items del plan ordenados por prioridad
       (principales primero, transversales al final).
    2. Para cada item, busca slots disponibles donde:
       - El docente asignado esté libre.
       - La ficha no tenga otro bloque.
    3. Crea el bloque y lo vincula al item del plan.
    4. Si no encuentra slot, registra el conflicto sin fallar.
    """

    def __init__(self, plan_trimestral, jornada, dias_disponibles=None):
        self.plan    = plan_trimestral
        self.jornada = jornada
        self.dias    = dias_disponibles or [
            BloqueHorario.DiaSemana.LUNES,
            BloqueHorario.DiaSemana.MARTES,
            BloqueHorario.DiaSemana.MIERCOLES,
            BloqueHorario.DiaSemana.JUEVES,
            BloqueHorario.DiaSemana.VIERNES,
        ]
        self.slots_base      = self._generar_slots_base()
        self.conflictos      = []
        self.bloques_creados = []

    def _generar_slots_base(self):
        """Genera slots de 2 horas según la jornada."""
        from datetime import time
        slots_por_jornada = {
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
        return slots_por_jornada.get(self.jornada, [])

    @transaction.atomic
    def generar(self) -> dict:
        items = self.plan.items.select_related(
            'competencia', 'docente__user'
        ).order_by(
            'competencia__tipo',  # PRINCIPAL primero
            'orden',
        )

        for item in items:
            horas_restantes = item.horas_asignadas
            for dia in self.dias:
                if horas_restantes <= 0:
                    break
                for h_inicio, h_fin in self.slots_base:
                    if horas_restantes <= 0:
                        break

                    disponibilidad = BloqueHorarioService.verificar_disponibilidad(
                        dia=dia,
                        hora_inicio=h_inicio,
                        hora_fin=h_fin,
                        docente=item.docente,
                        ficha=self.plan.ficha,
                    )

                    if not disponibilidad['disponible']:
                        continue

                    try:
                        bloque = BloqueHorarioService.crear_bloque({
                            'dia_semana':  dia,
                            'hora_inicio': h_inicio,
                            'hora_fin':    h_fin,
                            'jornada':     self.jornada,
                            'docente':     item.docente,
                            'ficha':       self.plan.ficha,
                        })
                        BloqueCompetencia.objects.create(   # FIX S1: sin import aquí
                            bloque=bloque,
                            item_plan=item,
                            horas_ejecutadas=2,
                        )
                        self.bloques_creados.append(bloque)
                        horas_restantes -= 2

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