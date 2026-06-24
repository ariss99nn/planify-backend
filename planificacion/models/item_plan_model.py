# planificacion/models/item_plan_model.py
from decimal import Decimal

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models


class ItemPlan(models.Model):
    """
    Cada competencia dentro de un PlanTrimestral.
    Puede ser principal (asignatura del programa) o transversal.
    """

    plan = models.ForeignKey(
        'planificacion.PlanTrimestral',
        on_delete=models.PROTECT,
        related_name='items',
    )
    competencia = models.ForeignKey(
        'competencia.Competencia',
        on_delete=models.PROTECT,
        related_name='items_plan',
    )
    docente = models.ForeignKey(
        'docentes.Docente',
        on_delete=models.PROTECT,
        related_name='items_plan',
        null=True, blank=True,
        help_text='Docente asignado a esta competencia en este trimestre.',
    )
    horas_asignadas = models.PositiveIntegerField(
        help_text='Horas totales planificadas para esta competencia.',
    )
    orden = models.PositiveIntegerField(
        help_text='Orden de dictado dentro del trimestre.',
    )
    completado = models.BooleanField(default=False)

    class Meta:
        verbose_name        = 'Ítem de plan'
        verbose_name_plural = 'Ítems de plan'
        unique_together     = [('plan', 'competencia')]
        ordering            = ['plan', 'orden']

    def __str__(self):
        return f"{self.plan} -- {self.competencia.codigo} ({self.horas_asignadas}h)"

    def clean(self):
        # 1. Horas positivas
        if self.horas_asignadas is not None and self.horas_asignadas <= 0:
            raise ValidationError(
                {'horas_asignadas': 'Las horas asignadas deben ser mayores a 0.'}
            )

        # 2. Horas no superan el tope de la asignatura
        if self.competencia_id and self.competencia.asignatura_id:
            asignatura = self.competencia.asignatura
            horas_max  = asignatura.total_horas
            if self.horas_asignadas and self.horas_asignadas > horas_max:
                raise ValidationError({
                    'horas_asignadas': (
                        f'No puede superar las {horas_max}h '
                        f'de la asignatura "{asignatura.nombre}".'
                    )
                })

        # 3. Habilitación del docente
        if self.docente_id and self.competencia_id:
            HabilitacionDocente = apps.get_model('docentes', 'HabilitacionDocente')
            competencia         = self.competencia
            tiene_habilitacion  = False

            if competencia.asignatura_id:
                tiene_habilitacion = HabilitacionDocente.objects.filter(
                    docente=self.docente,
                    nivel='ASIGNATURA',
                    asignatura=competencia.asignatura,
                    activo=True,
                ).exists()

                if not tiene_habilitacion:
                    tiene_habilitacion = HabilitacionDocente.objects.filter(
                        docente=self.docente,
                        nivel='MODULO',
                        modulo=competencia.asignatura.modulo,
                        activo=True,
                    ).exists()
            else:
                # Competencia transversal: basta con que el docente esté activo
                tiene_habilitacion = self.docente.estado

            if not tiene_habilitacion:
                raise ValidationError({
                    'docente': (
                        'El docente no tiene habilitación activa para '
                        'esta competencia.'
                    )
                })

    # ------------------------------------------------------------------
    # Properties de progreso — normalizados a Decimal para consistencia
    # con BloqueCompetencia.horas_ejecutadas (DecimalField).
    # ------------------------------------------------------------------

    @property
    def horas_ejecutadas(self) -> Decimal:
        from django.db.models import Sum
        result = self.bloques_ejecutados.aggregate(total=Sum('horas_ejecutadas'))
        return result['total'] or Decimal('0')

    @property
    def horas_restantes(self) -> Decimal:
        return max(Decimal('0'), Decimal(self.horas_asignadas) - self.horas_ejecutadas)

    @property
    def porcentaje_avance(self) -> float:
        if not self.horas_asignadas:
            return 0.0
        return round(float(self.horas_ejecutadas / Decimal(self.horas_asignadas)) * 100, 1)