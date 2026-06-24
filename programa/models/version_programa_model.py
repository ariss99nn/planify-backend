# programa/models/version_programa_model.py
from django.db import models
from programa.models.programa_model import Programa
from django.core.exceptions import ValidationError
from django.db import transaction
class VersionPrograma(models.Model):
    programa = models.ForeignKey(
        Programa,
        on_delete=models.PROTECT,
        related_name='versiones',
    )
    numero      = models.PositiveIntegerField(help_text='Numero de version. Ej: 1, 2.')
    descripcion = models.TextField(blank=True)
    vigente = models.BooleanField(default=False, db_index=True)
    fecha_inicio = models.DateField()
    fecha_fin    = models.DateField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name        = 'Version de programa'
        verbose_name_plural = 'Versiones de programa'
        ordering = ['programa', '-numero']
        unique_together = [('programa', 'numero')]

    def __str__(self):
        return f"{self.programa.nombre} v{self.numero}"

    # 1. clean() — no existe
    def clean(self):
        if self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({'fecha_fin': 'fecha_fin debe ser posterior a fecha_inicio.'})

    # 2. save() — sin full_clean() ni transaction.atomic()
    def save(self, *args, **kwargs):
        if self.vigente:
            with transaction.atomic():
                self.full_clean()
                VersionPrograma.objects.filter(
                    programa=self.programa, vigente=True,
                ).exclude(pk=self.pk).update(vigente=False)
                super().save(*args, **kwargs)
        else:
            self.full_clean()
            super().save(*args, **kwargs)

    # 3. total_horas — sigue sumando módulos INACTIVO
    @property
    def total_horas(self):
        from programa.models.modulo_model import Modulo
        return sum(
            m.total_horas
            for m in self.modulos.filter(estado=Modulo.Estado.ACTIVO)
        )