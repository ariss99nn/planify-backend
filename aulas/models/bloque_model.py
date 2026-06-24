from django.db import models
from django.core.exceptions import ValidationError
from users.validators import validate_imagen_5mb


class Bloque(models.Model):
    class Estado(models.TextChoices):
        ACTIVO        = 'ACT',  'Activo'
        MANTENIMIENTO = 'MANT', 'Mantenimiento'
        INACTIVO      = 'INAC', 'Inactivo'

    nombre           = models.CharField(max_length=50, unique=True)
    pisos            = models.PositiveIntegerField(
        help_text='Número de pisos del bloque.',
    )
    capacidad_maxima = models.PositiveIntegerField(
        help_text='Capacidad total de personas en el bloque.',
    )
    # CORRECCIÓN: se elimina db_index=True del campo porque ya existe
    # models.Index(fields=['estado']) en Meta → índice duplicado.
    estado      = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    descripcion = models.TextField(blank=True)
    imagen      = models.ImageField(
        upload_to='bloques/',
        null=True,
        blank=True,
        validators=[validate_imagen_5mb],
    )

    class Meta:
        verbose_name        = 'Bloque'
        verbose_name_plural = 'Bloques'
        ordering            = ['nombre']
        indexes = [
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return self.nombre

    def clean(self):
        errors = {}
        if self.capacidad_maxima is not None and self.capacidad_maxima <= 0:
            errors['capacidad_maxima'] = 'La capacidad debe ser mayor a 0.'
        if self.pisos is not None and self.pisos <= 0:
            errors['pisos'] = 'El número de pisos debe ser mayor a 0.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)