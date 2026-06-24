# docentes/models/docente_disponibilidad_model.py
from django.db import models
from django.core.exceptions import ValidationError

class Disponibilidad(models.Model):
    """
    Restricción horaria de un docente ANTES de generar el horario.
    No depende de BloqueHorario: es una declaración previa de disponibilidad.

    disponible=True  → el docente puede ser asignado en ese slot.
    disponible=False → el docente NO puede; requiere motivo.

    El motor de horarios lee estas disponibilidades para respetar
    restricciones al generar BloqueHorario.
    """

    class DiaSemana(models.TextChoices):
        LUNES     = 'LUNES',     'Lunes'
        MARTES    = 'MARTES',    'Martes'
        MIERCOLES = 'MIERCOLES', 'Miércoles'
        JUEVES    = 'JUEVES',    'Jueves'
        VIERNES   = 'VIERNES',   'Viernes'
        SABADO    = 'SABADO',    'Sábado'

    class TipoRestriccion(models.TextChoices):
        PERMANENTE = 'PERMANENTE', 'Permanente (toda la vigencia)'
        TEMPORAL   = 'TEMPORAL',   'Temporal (rango de fechas)'

    docente = models.ForeignKey(
        'docentes.Docente',
        on_delete=models.CASCADE,
        related_name='disponibilidades',
    )
    dia_semana = models.CharField(
        max_length=10,
        choices=DiaSemana.choices,
        db_index=True,
    )
    hora_inicio = models.TimeField()
    hora_fin    = models.TimeField()

    disponible = models.BooleanField(
        default=True,
        help_text='False = el docente no puede en este slot.',
    )
    motivo = models.TextField(
        blank=True,
        help_text='Obligatorio cuando disponible=False.',
    )

    tipo_restriccion = models.CharField(
        max_length=12,
        choices=TipoRestriccion.choices,
        default=TipoRestriccion.PERMANENTE,
        db_index=True,
    )
    fecha_inicio_restriccion = models.DateField(
        null=True, blank=True,
        help_text='Solo si tipo_restriccion=TEMPORAL.',
    )
    fecha_fin_restriccion = models.DateField(
        null=True, blank=True,
        help_text='Solo si tipo_restriccion=TEMPORAL.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Disponibilidad'
        verbose_name_plural = 'Disponibilidades'
        unique_together = [('docente', 'dia_semana', 'hora_inicio', 'hora_fin')]
        ordering = ['docente', 'dia_semana', 'hora_inicio']
        indexes = [
            models.Index(fields=['docente', 'dia_semana']),
            models.Index(fields=['disponible']),
        ]

    def __str__(self):
        estado = 'Disponible' if self.disponible else 'No disponible'
        return (
            f"{self.docente} — {self.get_dia_semana_display()} "
            f"{self.hora_inicio}–{self.hora_fin} ({estado})"
        )

    def clean(self):
        # Validación de horas
        if self.hora_inicio and self.hora_fin:
            if self.hora_inicio >= self.hora_fin:
                raise ValidationError({
                    'hora_fin': 'La hora de fin debe ser mayor a la hora de inicio.'
                })
            self._validar_solapamiento()

        # Motivo obligatorio si no disponible
        if not self.disponible and not self.motivo:
            raise ValidationError({
                'motivo': 'Debe especificar un motivo si no está disponible.'
            })

        # Validaciones de restricción temporal
        if self.tipo_restriccion == self.TipoRestriccion.TEMPORAL:
            if not self.fecha_inicio_restriccion or not self.fecha_fin_restriccion:
                raise ValidationError({
                    'fecha_inicio_restriccion': (
                        'Las restricciones temporales requieren '
                        'fecha de inicio y fin.'
                    )
                })
            if self.fecha_fin_restriccion <= self.fecha_inicio_restriccion:
                raise ValidationError({
                    'fecha_fin_restriccion': (
                        'La fecha de fin debe ser posterior a la de inicio.'
                    )
                })
        else:
            # Limpiar fechas si no es temporal
            self.fecha_inicio_restriccion = None
            self.fecha_fin_restriccion = None

    def _validar_solapamiento(self):
        if not self.docente_id:
            return
        qs = Disponibilidad.objects.filter(
            docente_id=self.docente_id,
            dia_semana=self.dia_semana,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio,
        ).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({
                'hora_inicio': (
                    'El docente ya tiene un slot de disponibilidad '
                    'que se solapa con este horario.'
                )
            })

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)