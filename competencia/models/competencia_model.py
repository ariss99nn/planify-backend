# competencia/models/competencia_model.py
from django.db import models
from django.core.exceptions import ValidationError
from competencia.models.asignatura_model import Asignatura


class Competencia(models.Model):

    class TipoCompetencia(models.TextChoices):
        PRINCIPAL    = 'PRINCIPAL',    'Principal'
        TRANSVERSAL  = 'TRANSVERSAL',  'Transversal'

    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.PROTECT,
        related_name='competencias',
        null=True,
        blank=True,
        help_text='Null si es transversal (pertenece al centro, no a un módulo).',
    )
    tipo = models.CharField(
        max_length=15,
        choices=TipoCompetencia.choices,
        default=TipoCompetencia.PRINCIPAL,
        db_index=True,
    )
    es_induccion = models.BooleanField(
        default=False,
        help_text='Marca esta competencia transversal como inducción obligatoria en trimestre 1.',
    )
    induccion_activa = models.BooleanField(
        default=True,
        help_text='Permite al administrador desactivar la inducción.',
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        help_text='Código único. Ej: COMP-001.',
    )
    nombre      = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    horas_trimestre_transversal = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Solo aplica para competencias transversales.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Competencia'
        verbose_name_plural = 'Competencias'
        ordering            = ['tipo', 'codigo']
        
    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.codigo} — {self.nombre}"

    def clean(self):
        if self.tipo == self.TipoCompetencia.PRINCIPAL:
            if not self.asignatura_id:
                raise ValidationError(
                    {'asignatura': 'Las competencias principales deben tener una asignatura.'}
                )
            # CORRECCIÓN: horas_trimestre_transversal debe ser null para principales
            if self.horas_trimestre_transversal is not None:
                raise ValidationError(
                    {'horas_trimestre_transversal': 'Este campo solo aplica a competencias transversales.'}
                )

        if self.tipo == self.TipoCompetencia.TRANSVERSAL:
            if self.asignatura_id:
                raise ValidationError(
                    {'asignatura': 'Las competencias transversales no pertenecen a una asignatura.'}
                )
            # CORRECCIÓN: transversales deben definir sus horas
            if self.horas_trimestre_transversal is None:
                raise ValidationError(
                    {'horas_trimestre_transversal': 'Las competencias transversales deben tener horas definidas.'}
                )
        if self.es_induccion and self.tipo != self.TipoCompetencia.TRANSVERSAL:
            raise ValidationError({'es_induccion': 'Solo competencias transversales pueden ser inducción.'})
    
    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)
        