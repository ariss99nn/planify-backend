# ficha/models/ficha_reasignacion_model.py
from django.db import models
from django.conf import settings
from ficha.models.ficha_model import Ficha
from django.core.exceptions import ValidationError
from ficha.models.ficha_estudiante_model import FichaEstudiante

class ReasignacionFicha(models.Model):
    
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reasignaciones',
        limit_choices_to={'rol': 'ESTUDIANTE'},
    )
    ficha_origen = models.ForeignKey(
        Ficha,
        on_delete=models.PROTECT,
        related_name='reasignaciones_salida',
    )
    ficha_destino = models.ForeignKey(
        Ficha,
        on_delete=models.PROTECT,
        related_name='reasignaciones_entrada',
    )
    motivo = models.TextField(
        help_text='Motivo de la reasignación (cambio de jornada, cupo, etc.).',
    )
    realizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reasignaciones_realizadas',
        null=True,
        blank=True,
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reasignación de ficha'
        verbose_name_plural = 'Reasignaciones de ficha'
        ordering = ['-fecha']

    def __str__(self):
        return (
            f"{self.estudiante.nombre}: "
            f"{self.ficha_origen.codigo_ficha} → "
            f"{self.ficha_destino.codigo_ficha}"
        )

    def clean(self):
        if not self.ficha_origen_id or not self.ficha_destino_id:
            return
        if self.ficha_origen_id == self.ficha_destino_id:
            raise ValidationError('Origen y destino no pueden ser la misma ficha.')
        if self.ficha_origen.version.programa != self.ficha_destino.version.programa:
            raise ValidationError('Las fichas deben pertenecer al mismo programa.')
        if not FichaEstudiante.objects.filter(
            ficha=self.ficha_origen, estudiante=self.estudiante, activo=True
        ).exists():
            raise ValidationError('El estudiante no está activo en la ficha de origen.')
    
    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)