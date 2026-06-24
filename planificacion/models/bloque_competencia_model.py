# planificacion/models/bloque_competencia_model.py
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class BloqueCompetencia(models.Model):
    """
    Vincula un BloqueHorario con el ItemPlan que ejecuta.
    Es el puente entre el horario físico y el plan curricular.
    """

    bloque = models.OneToOneField(
        'bhorario.BloqueHorario',
        on_delete=models.PROTECT,
        related_name='competencia_asignada',
    )
    item_plan = models.ForeignKey(
        'planificacion.ItemPlan',
        on_delete=models.PROTECT,
        related_name='bloques_ejecutados',
    )
    horas_ejecutadas = models.DecimalField(
        max_digits=4, decimal_places=1,
        help_text='Horas reales ejecutadas en este bloque.',
    )
    observaciones = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Bloque de competencia'
        verbose_name_plural = 'Bloques de competencia'

    def __str__(self):
        return f"{self.bloque} -> {self.item_plan.competencia.codigo}"

    def clean(self):
        if (
            self.horas_ejecutadas is not None
            and self.horas_ejecutadas <= Decimal('0')
        ):
            raise ValidationError(
                {'horas_ejecutadas': 'Las horas ejecutadas deben ser mayores a 0.'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)