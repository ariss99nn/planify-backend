# competencia/models/resultado_aprendizaje_model.py
from django.db import models
from competencia.models.competencia_model import Competencia


class ResultadoAprendizaje(models.Model):

    competencia = models.ForeignKey(
        Competencia,
        on_delete=models.PROTECT,
        related_name='resultados',
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        help_text='Código único. Ej: RAP-001.',
    )
    descripcion          = models.TextField()
    criterios_evaluacion = models.TextField(
        blank=True,
        help_text='Criterios con los que se evalúa el resultado.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Resultado de aprendizaje'
        verbose_name_plural = 'Resultados de aprendizaje'
        ordering            = ['competencia', 'codigo']

    def __str__(self):
        return f"{self.codigo} — {self.descripcion[:60]}"
    
    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)