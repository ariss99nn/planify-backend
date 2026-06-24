# planificacion/models/plan_trimestral_model.py
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class PlanTrimestral(models.Model):

    class EstadoPlan(models.TextChoices):
        BORRADOR     = 'BORRADOR',     'Borrador'
        EN_REVISION  = 'EN_REVISION',  'En revisión'
        APROBADO     = 'APROBADO',     'Aprobado'
        EN_EJECUCION = 'EN_EJECUCION', 'En ejecución'
        CERRADO      = 'CERRADO',      'Cerrado'
        RECHAZADO    = 'RECHAZADO',    'Rechazado'

    estado = models.CharField(
        max_length=15,
        choices=EstadoPlan.choices,
        default=EstadoPlan.BORRADOR,
        db_index=True,
    )
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='planes_aprobados',
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    motivo_rechazo = models.TextField(
        blank=True,
        help_text='Obligatorio si estado=RECHAZADO.',
    )

    ficha = models.ForeignKey(
        'ficha.Ficha',
        on_delete=models.PROTECT,
        related_name='planes_trimestrales',
    )
    trimestre = models.PositiveIntegerField(
        help_text='Número de trimestre al que aplica este plan.',
    )
    fecha_inicio = models.DateField()
    fecha_fin    = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Plan trimestral'
        verbose_name_plural = 'Planes trimestrales'
        unique_together     = [('ficha', 'trimestre')]
        ordering            = ['ficha', 'trimestre']

    def __str__(self):
        return f"Ficha {self.ficha.codigo_ficha} -- Trimestre {self.trimestre}"

    def clean(self):
        # 1. Coherencia de fechas
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError(
                {'fecha_fin': 'La fecha de fin debe ser posterior a la de inicio.'}
            )

        # 2. Trimestre dentro del rango del programa
        if self.ficha_id:
            ficha    = self.ficha
            programa = ficha.version.programa
            if ficha.cadena_formacion and programa.trimestres_cadena:
                trimestres_max = programa.trimestres_cadena
            else:
                trimestres_max = programa.trimestres_totales
            if self.trimestre > trimestres_max:
                raise ValidationError({
                    'trimestre': (
                        f'El trimestre no puede superar {trimestres_max} '
                        f'para este programa.'
                    )
                })

        # 3. Motivo de rechazo obligatorio
        if self.estado == self.EstadoPlan.RECHAZADO and not self.motivo_rechazo:
            raise ValidationError({
                'motivo_rechazo': 'Debe indicar el motivo del rechazo.'
            })

        # 4. Aprobador obligatorio en estados post-aprobación
        if self.estado in (
            self.EstadoPlan.APROBADO,
            self.EstadoPlan.EN_EJECUCION,
            self.EstadoPlan.CERRADO,
        ) and not self.aprobado_por_id:
            raise ValidationError({
                'aprobado_por': 'Debe registrar quién aprobó el plan.'
            })

    def save(self, *args, **kwargs):
        # Sólo omitir full_clean cuando se actualicen campos específicos
        # (p.ej. transiciones de estado desde el serializer/service).
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # Properties de progreso — se normalizan a Decimal para evitar
    # errores de tipo al mezclar DecimalField con PositiveIntegerField.
    # ------------------------------------------------------------------

    @property
    def total_horas_planificadas(self) -> Decimal:
        from django.db.models import Sum
        result = self.items.aggregate(total=Sum('horas_asignadas'))
        return Decimal(result['total'] or 0)

    @property
    def total_horas_ejecutadas(self) -> Decimal:
        from django.apps import apps
        from django.db.models import Sum
        BloqueCompetencia = apps.get_model('planificacion', 'BloqueCompetencia')
        result = BloqueCompetencia.objects.filter(
            item_plan__plan=self
        ).aggregate(total=Sum('horas_ejecutadas'))
        return result['total'] or Decimal('0')

    @property
    def porcentaje_avance(self) -> float:
        total = self.total_horas_planificadas
        if not total:
            return 0.0
        return round(float(self.total_horas_ejecutadas / total) * 100, 1)