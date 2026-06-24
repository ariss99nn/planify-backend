# programa/models/modulo_model.py
from django.db import models
from programa.models.version_programa_model import VersionPrograma
from django.core.exceptions import ValidationError

class Modulo(models.Model):

    class Estado(models.TextChoices):
        ACTIVO   = 'ACTIVO',   'Activo'
        INACTIVO = 'INACTIVO', 'Inactivo'

    version = models.ForeignKey(
        VersionPrograma,
        on_delete=models.PROTECT,
        related_name='modulos',
    )
    nombre      = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    orden       = models.PositiveIntegerField(
        help_text='Posicion del modulo dentro de la version.',
    )
    horas_lectivas  = models.PositiveIntegerField()
    horas_practicas = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices,
        default=Estado.ACTIVO, db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Modulo'
        verbose_name_plural = 'Modulos'
        ordering = ['version', 'orden']
        unique_together = [('version', 'orden')]

    def __str__(self):
        return f"{self.version} -- {self.nombre}"
    def clean(self):
        if self.horas_lectivas is not None and self.horas_lectivas <= 0:
            raise ValidationError({'horas_lectivas': 'Debe ser mayor a 0.'})
        if self.horas_practicas is not None and self.horas_practicas < 0:
            raise ValidationError({'horas_practicas': 'No puede ser negativo.'})

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)
        
    @property
    def total_horas(self):
        return self.horas_lectivas + self.horas_practicas