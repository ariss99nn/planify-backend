#alertas/models/alerta_model.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class Alerta(models.Model):

    class TipoAlerta(models.TextChoices):
        CONFLICTO      = 'CONFLICTO',      'Conflicto de horario'
        DISPONIBILIDAD = 'DISPONIBILIDAD', 'Disponibilidad'
        SISTEMA        = 'SISTEMA',        'Sistema'

    class FormatoAlerta(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS   = 'SMS',   'SMS'
        APP   = 'APP',   'Notificación App'

    class EstadoAlerta(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ENVIADA   = 'ENVIADA',   'Enviada'
        LEIDA     = 'LEIDA',     'Leída'

    tipo = models.CharField(
        max_length=20,
        choices=TipoAlerta.choices,
        db_index=True,
    )
    descripcion = models.TextField()
    formato_alerta = models.CharField(
        max_length=10,
        choices=FormatoAlerta.choices,
        default=FormatoAlerta.APP,
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadoAlerta.choices,
        default=EstadoAlerta.PENDIENTE,
        db_index=True,
    )
    bloque_origen = models.ForeignKey(
        'bhorario.BloqueHorario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas',
    )
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='alertas',
        null=True,
        blank=True,
        help_text='Usuario al que va dirigida la alerta.',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Momento en que el usuario leyó la alerta.',
    )

    class Meta:
        verbose_name        = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado', 'tipo']),
            models.Index(fields=['destinatario', 'estado']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.get_estado_display()}"

    def clean(self):
        if (
            self.tipo == self.TipoAlerta.CONFLICTO
            and not self.bloque_origen_id
        ):
            raise ValidationError(
                {'bloque_origen': 'Las alertas de conflicto deben tener un bloque origen.'}
            )
        if self.tipo != self.TipoAlerta.SISTEMA and not self.destinatario_id:
            raise ValidationError(
                {'destinatario': 'Obligatorio para alertas que no son de sistema.'}
            )

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)

    def marcar_leida(self):
        """Marca la alerta como leída si aún no lo está."""
        if self.estado != self.EstadoAlerta.LEIDA:
            self.estado = self.EstadoAlerta.LEIDA
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['estado', 'fecha_lectura'])