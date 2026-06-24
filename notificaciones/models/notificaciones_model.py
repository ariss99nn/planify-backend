# notificaciones/models/notificaciones_model.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class Notificacion(models.Model):

    class Canal(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS   = 'SMS',   'SMS'
        APP   = 'APP',   'Notificación App'

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ENVIADA   = 'ENVIADA',   'Enviada'
        FALLIDA   = 'FALLIDA',   'Fallida'

    alerta = models.ForeignKey(
        'alertas.Alerta',
        on_delete=models.CASCADE,
        related_name='notificaciones',
    )
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones_recibidas',
    )
    canal = models.CharField(
        max_length=10,
        choices=Canal.choices,
        default=Canal.APP,
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        db_index=True,
    )
    intentos = models.PositiveSmallIntegerField(default=0)
    error_detalle = models.TextField(blank=True)
    tarea_id = models.CharField(max_length=255, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio    = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado', 'canal']),
            models.Index(fields=['destinatario', 'estado']),
        ]
        unique_together = [('alerta', 'destinatario', 'canal')]

    def __str__(self):
        return (
            f"Notif. {self.canal} → {self.destinatario_id} "
            f"[{self.get_estado_display()}]"
        )

    def marcar_enviada(self):
        self.estado      = self.Estado.ENVIADA
        self.fecha_envio = timezone.now()
        self.intentos   += 1
        self.save(update_fields=['estado', 'fecha_envio', 'intentos'])

    def marcar_fallida(self, detalle: str = ''):
        self.estado        = self.Estado.FALLIDA
        self.intentos     += 1
        self.error_detalle = detalle
        self.save(update_fields=['estado', 'intentos', 'error_detalle'])