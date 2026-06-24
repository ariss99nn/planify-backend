# planificacion/services/plan_service.py
import logging

from django.db import transaction

from planificacion.models.item_plan_model import ItemPlan
from planificacion.models.plan_trimestral_model import PlanTrimestral

logger = logging.getLogger(__name__)


class PlanService:

    @staticmethod
    @transaction.atomic
    def aprobar_plan(plan: PlanTrimestral, usuario) -> PlanTrimestral:
        """
        Aprobación programática (p.ej. desde un comando de gestión).
        Para aprobaciones vía API se usa PlanTrimestralCambiarEstadoSerializer,
        que ya centraliza las validaciones de transición.

        CORRECCIÓN: se verifica que el estado previo sea EN_REVISION,
        que es el único estado desde el que se puede aprobar según el flujo.
        """
        if plan.estado != PlanTrimestral.EstadoPlan.EN_REVISION:
            raise ValueError(
                f'Solo se puede aprobar un plan en estado EN_REVISION. '
                f'Estado actual: {plan.estado}.'
            )
        if not plan.items.exists():
            raise ValueError('No se puede aprobar un plan sin ítems.')

        from django.utils import timezone

        plan.estado           = PlanTrimestral.EstadoPlan.APROBADO
        plan.aprobado_por     = usuario
        plan.fecha_aprobacion = timezone.now()
        plan.save(update_fields=['estado', 'aprobado_por', 'fecha_aprobacion'])

        logger.info("Plan %s aprobado por %s", plan, usuario.email)
        return plan

    @staticmethod
    def calcular_carga_docente(docente, trimestre: int) -> dict:
        """Calcula las horas asignadas a un docente en un trimestre."""
        items = ItemPlan.objects.filter(
            docente=docente,
            plan__trimestre=trimestre,
            plan__estado__in=[
                PlanTrimestral.EstadoPlan.APROBADO,
                PlanTrimestral.EstadoPlan.EN_EJECUCION,
            ],
        ).select_related('competencia', 'plan__ficha')

        total_horas = sum(i.horas_asignadas for i in items)
        max_horas   = docente.horas_max_semanales * 12  # 12 semanas por trimestre

        # CORRECCIÓN: acceso seguro a nombre del docente
        nombre_docente = (
            docente.user.nombre
            if hasattr(docente, 'user') and docente.user
            else str(docente)
        )

        return {
            'docente': nombre_docente,
            'trimestre': trimestre,
            'horas_planificadas': total_horas,
            'horas_maximas': max_horas,
            'porcentaje_carga': (
                round((total_horas / max_horas) * 100, 1) if max_horas else 0
            ),
            'sobrecargado': total_horas > max_horas,
            'items': [
                {
                    'ficha':       i.plan.ficha.codigo_ficha,
                    'competencia': i.competencia.codigo,
                    'horas':       i.horas_asignadas,
                }
                for i in items
            ],
        }