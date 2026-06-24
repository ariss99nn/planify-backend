from django.db import models
from django.core.exceptions import ValidationError
from .bloque_model import Bloque
from .equipamiento_model import Equipamiento
from users.validators import validate_imagen_5mb


class Aula(models.Model):
    class TipoAula(models.TextChoices):
        LABORATORIO = 'LAB', 'Laboratorio'
        TEORICA     = 'TEO', 'Teórica'
        SISTEMAS    = 'SIS', 'Sistemas de Información'
        OTRO        = 'OTR', 'Otro'

    class Estado(models.TextChoices):
        ACTIVA        = 'ACT',  'Activa'
        MANTENIMIENTO = 'MANT', 'Mantenimiento'
        INACTIVA      = 'INAC', 'Inactiva'

    codigo_aula = models.CharField(max_length=10, unique=True, db_index=True)
    capacidad   = models.PositiveIntegerField()
    tipo_aula   = models.CharField(max_length=10, choices=TipoAula.choices)
    estado      = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVA,
    )
    bloque = models.ForeignKey(
        Bloque,
        on_delete=models.PROTECT,
        related_name='aulas',
    )
    piso        = models.PositiveIntegerField(
        help_text='Piso del bloque donde se ubica el aula.',
    )
    descripcion = models.TextField(blank=True)
    imagen      = models.ImageField(
        upload_to='aulas/',
        null=True,
        blank=True,
        validators=[validate_imagen_5mb],
    )
    equipamiento = models.ManyToManyField(
        Equipamiento,
        blank=True,
        related_name='aulas',
    )

    class Meta:
        verbose_name        = 'Aula'
        verbose_name_plural = 'Aulas'
        ordering            = ['bloque', 'codigo_aula']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_aula']),
            models.Index(fields=['bloque', 'estado']),
        ]

    def __str__(self):
        return f"{self.codigo_aula} — {self.bloque.nombre}"

    def clean(self):
        errors = {}

        if self.capacidad is not None and self.capacidad <= 0:
            errors['capacidad'] = 'La capacidad debe ser mayor a 0.'

        if self.bloque_id:
            try:
                bloque = self.bloque

                # CORRECCIÓN: la validación de piso aplica siempre que haya
                # bloque asignado, no solo cuando el aula está ACTIVA.
                if self.piso is not None and self.piso > bloque.pisos:
                    errors['piso'] = (
                        'El piso no puede superar el número de pisos del bloque '
                        f'({bloque.pisos}).'
                    )

                # Un aula ACTIVA no puede pertenecer a un bloque inactivo.
                if (
                    self.estado == self.Estado.ACTIVA
                    and bloque.estado == Bloque.Estado.INACTIVO
                ):
                    errors['estado'] = (
                        'No se puede tener un aula activa en un bloque inactivo.'
                    )

            except Bloque.DoesNotExist:
                pass

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)