# ficha/models/ficha_estudiante_model.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from ficha.models.ficha_model import Ficha


class FichaEstudiante(models.Model):

    class MotivoRetiro(models.TextChoices):
        DESERCION         = 'DESERCION',         'Deserción'
        RETIRO_VOLUNTARIO = 'RETIRO_VOLUNTARIO',  'Retiro voluntario'
        CANCELADO         = 'CANCELADO',          'Cancelado por rendimiento'
        GRADUADO          = 'GRADUADO',           'Graduado'
        REASIGNADO        = 'REASIGNADO',         'Reasignado a otra ficha'

    ficha = models.ForeignKey(
        Ficha,
        on_delete=models.PROTECT,
        related_name='estudiantes',
    )
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='fichas_asignadas',
        limit_choices_to={'rol': 'ESTUDIANTE'},
    )
    activo       = models.BooleanField(default=True, db_index=True)
    es_cadena    = models.BooleanField(
        default=False,
        help_text=(
            'True si el estudiante ingresó por cadena de formación '
            '(reduce tiempo en etapa lectiva).'
        ),
    )
    fecha_ingreso  = models.DateField(auto_now_add=True)
    fecha_retiro   = models.DateField(null=True, blank=True)
    motivo_retiro  = models.CharField(
        max_length=20,
        choices=MotivoRetiro.choices,
        null=True,
        blank=True,
        db_index=True,
        help_text='Obligatorio al desactivar al estudiante.',
    )

    class Meta:
        verbose_name        = 'Estudiante en ficha'
        verbose_name_plural = 'Estudiantes en ficha'
        unique_together     = [('ficha', 'estudiante')]
        ordering            = ['ficha', 'estudiante__nombre']
        indexes = [
            models.Index(fields=['activo']),
            models.Index(fields=['es_cadena']),
            models.Index(fields=['motivo_retiro']),
        ]

    def __str__(self):
        return f"{self.estudiante.nombre} → Ficha {self.ficha.codigo_ficha}"

    def clean(self):
        # ── Coherencia cadena ────────────────────────────────────────────
        # FIX: ambos bloques protegidos con self.ficha_id para evitar
        # RelatedObjectDoesNotExist cuando la FK aún no está resuelta.
        if self.ficha_id:
            if self.ficha.cadena_formacion and not self.es_cadena:
                raise ValidationError({
                    'es_cadena': 'La ficha es de cadena; el estudiante debe marcarse igual.'
                })
            if not self.ficha.cadena_formacion and self.es_cadena:
                raise ValidationError({
                    'es_cadena': 'La ficha no es de cadena de formación.'
                })

        # ── Unicidad de ficha activa ─────────────────────────────────────
        if self.activo:
            if FichaEstudiante.objects.filter(
                estudiante=self.estudiante,
                activo=True,
            ).exclude(pk=self.pk).exists():
                raise ValidationError('El estudiante ya tiene una ficha activa.')

        # ── Datos de retiro obligatorios ─────────────────────────────────
        if not self.activo:
            if not self.fecha_retiro:
                raise ValidationError({'fecha_retiro': 'Obligatoria al desactivar.'})
            if not self.motivo_retiro:
                raise ValidationError({'motivo_retiro': 'Obligatorio al desactivar.'})

    def save(self, *args, **kwargs):
        # FIX: respetar update_fields igual que Ficha.save() para no romper
        # actualizaciones parciales (ej. _relacion_origen.save(update_fields=[...])
        # dentro de ReasignacionCreateSerializer).
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)