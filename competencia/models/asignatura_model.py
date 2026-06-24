# competencia/models/asignatura_model.py
from django.db import models
from django.core.exceptions import ValidationError
from programa.models.modulo_model import Modulo

class Asignatura(models.Model):

    class Tipo(models.TextChoices):
        TEORICA           = 'TEORICA',           'Teórica'
        PRACTICA          = 'PRACTICA',          'Práctica'
        TEORICO_PRACTICA  = 'TEORICO_PRACTICA',  'Teórico-Práctica'

    class Estado(models.TextChoices):
        ACTIVA   = 'ACTIVA',   'Activa'
        INACTIVA = 'INACTIVA', 'Inactiva'

    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.PROTECT,
        related_name='asignaturas',
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.TEORICO_PRACTICA,
        db_index=True,
    )
    horas_lectivas  = models.PositiveIntegerField()
    horas_practicas = models.PositiveIntegerField()
    orden = models.PositiveIntegerField(
        help_text='Posición de la asignatura dentro del módulo.',
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVA,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Asignatura'
        verbose_name_plural = 'Asignaturas'
        ordering            = ['modulo', 'orden']
        unique_together     = [('modulo', 'orden')]

    def __str__(self):
        return f"{self.modulo.nombre} — {self.nombre}"

    def clean(self):
        if self.horas_lectivas is not None and self.horas_lectivas <= 0:
            raise ValidationError({'horas_lectivas': 'Las horas lectivas deben ser mayores a 0.'})
        if self.horas_practicas is not None and self.horas_practicas < 0:
            raise ValidationError({'horas_practicas': 'Las horas prácticas no pueden ser negativas.'})
    
    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)
        
    @property
    def total_horas(self):
        return self.horas_lectivas + self.horas_practicas