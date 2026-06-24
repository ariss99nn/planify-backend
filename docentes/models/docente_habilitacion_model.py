# docentes/models/docente_habilitacion_model.py
from django.db import models
from django.core.exceptions import ValidationError


class HabilitacionDocente(models.Model):
    """
    Catálogo de qué puede dictar un docente.
    Reemplaza DocenteModulo y DocenteAsignatura.

    Nivel MODULO  → docente cubre el módulo completo.
    Nivel ASIGNATURA → docente cubre solo esa asignatura.

    ItemPlan.docente debe validarse contra esta tabla antes de guardar.
    """

    class Nivel(models.TextChoices):
        MODULO     = 'MODULO',     'Módulo completo'
        ASIGNATURA = 'ASIGNATURA', 'Asignatura específica'

    docente = models.ForeignKey(
        'docentes.Docente',
        on_delete=models.CASCADE,
        related_name='habilitaciones',
    )
    nivel = models.CharField(
        max_length=12,
        choices=Nivel.choices,
        db_index=True,
    )
    modulo = models.ForeignKey(
        'programa.Modulo',
        on_delete=models.PROTECT,
        related_name='habilitaciones_docentes',
        null=True, blank=True,
    )
    asignatura = models.ForeignKey(
        'competencia.Asignatura',
        on_delete=models.PROTECT,
        related_name='habilitaciones_docentes',
        null=True, blank=True,
    )
    activo = models.BooleanField(default=True, db_index=True)
    fecha_desde = models.DateField(
        help_text='Fecha desde la que aplica esta habilitación.',
    )
    fecha_hasta = models.DateField(
        null=True, blank=True,
        help_text='Dejar en blanco si es indefinida.',
    )
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Habilitación docente'
        verbose_name_plural = 'Habilitaciones docentes'
        ordering = ['docente', 'nivel', 'modulo', 'asignatura']
        indexes = [
            models.Index(fields=['docente', 'nivel', 'activo']),
            models.Index(fields=['modulo', 'activo']),
            models.Index(fields=['asignatura', 'activo']),
        ]
        constraints = [
            # Evita duplicar la misma habilitación activa para un docente.
            # activo=False → historial, puede haber múltiples.
            # activo=True  → solo una por docente+módulo o docente+asignatura.
            # La reactivación (False→True) pasa por save() → full_clean() → clean(),
            # que valida fechas. El constraint de BD garantiza unicidad en activos.
            models.UniqueConstraint(
                fields=['docente', 'modulo'],
                condition=models.Q(nivel='MODULO', activo=True),
                name='unique_habilitacion_modulo_activa',
            ),
            models.UniqueConstraint(
                fields=['docente', 'asignatura'],
                condition=models.Q(nivel='ASIGNATURA', activo=True),
                name='unique_habilitacion_asignatura_activa',
            ),
        ]

    def __str__(self):
        target = self.modulo or self.asignatura or '(sin asignar)'
        return (
            f"{self.docente} — {self.get_nivel_display()}: "
            f"{target}"
        )

    def clean(self):
        if self.nivel == self.Nivel.MODULO:
            if not self.modulo_id:
                raise ValidationError({
                    'modulo': 'Habilitaciones de módulo requieren un módulo.'
                })
            if self.asignatura_id:
                raise ValidationError({
                    'asignatura': (
                        'Habilitaciones de módulo no deben tener asignatura.'
                    )
                })
            # Evita reactivar si ya existe otra activa para el mismo docente+módulo
            if self.activo and self.docente_id and self.modulo_id:
                if HabilitacionDocente.objects.filter(
                    docente_id=self.docente_id,
                    modulo_id=self.modulo_id,
                    nivel=self.Nivel.MODULO,
                    activo=True,
                ).exclude(pk=self.pk).exists():
                    raise ValidationError({
                        'activo': (
                            'Ya existe una habilitación activa para este '
                            'docente y módulo.'
                        )
                    })

        if self.nivel == self.Nivel.ASIGNATURA:
            if not self.asignatura_id:
                raise ValidationError({
                    'asignatura': (
                        'Habilitaciones de asignatura requieren una asignatura.'
                    )
                })
            if self.modulo_id:
                raise ValidationError({
                    'modulo': (
                        'Habilitaciones de asignatura no deben tener módulo.'
                    )
                })
            # Evita reactivar si ya existe otra activa para el mismo docente+asignatura
            if self.activo and self.docente_id and self.asignatura_id:
                if HabilitacionDocente.objects.filter(
                    docente_id=self.docente_id,
                    asignatura_id=self.asignatura_id,
                    nivel=self.Nivel.ASIGNATURA,
                    activo=True,
                ).exclude(pk=self.pk).exists():
                    raise ValidationError({
                        'activo': (
                            'Ya existe una habilitación activa para este '
                            'docente y asignatura.'
                        )
                    })

        if self.fecha_hasta and self.fecha_desde:
            if self.fecha_hasta <= self.fecha_desde:
                raise ValidationError({
                    'fecha_hasta': (
                        'La fecha de fin debe ser posterior a la de inicio.'
                    )
                })

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)