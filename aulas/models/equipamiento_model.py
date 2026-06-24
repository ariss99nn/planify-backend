from django.db import models
from django.core.exceptions import ValidationError
from users.validators import validate_imagen_5mb


class Equipamiento(models.Model):
    class Estado(models.TextChoices):
        FUNCIONAL     = 'FUNC', 'Funcional'
        DANADO        = 'DAN',  'Dañado'
        MANTENIMIENTO = 'MANT', 'En mantenimiento'

    nombre            = models.CharField(max_length=100)
    descripcion       = models.TextField(blank=True)
    cantidad          = models.PositiveIntegerField(
        default=1,
        help_text='Cantidad de unidades de este equipamiento.',
    )
    numero_serie      = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text='Número de serie. Opcional para ítems genéricos.',
    )
    fecha_adquisicion = models.DateField(null=True, blank=True)
    estado            = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.FUNCIONAL,
        db_index=True,
    )
    imagen = models.ImageField(
        upload_to='equipamiento/',
        null=True,
        blank=True,
        validators=[validate_imagen_5mb],
    )

    class Meta:
        verbose_name        = 'Equipamiento'
        verbose_name_plural = 'Equipamientos'
        ordering            = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"

    def clean(self):
        if self.cantidad is not None and self.cantidad <= 0:
            raise ValidationError({'cantidad': 'La cantidad debe ser mayor a 0.'})

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)