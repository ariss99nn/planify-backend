# programa/models/programa_model.py
from django.db import models
from django.core.exceptions import ValidationError

class Programa(models.Model):
    class Nivel(models.TextChoices):
        TECNICO     = 'TECNICO',     'Tecnico'
        TECNOLOGIA  = 'TECNOLOGIA',  'Tecnologia'
        CURSO_CORTO = 'CURSO_CORTO', 'Curso Corto'
    class Estado(models.TextChoices):
        ACTIVO     = 'ACTIVO',     'Activo'
        INACTIVO   = 'INACTIVO',   'Inactivo'
        EN_REVISION= 'EN_REVISION','En revision'
    class TipoFormacion(models.TextChoices):
        POR_OFERTA       = 'POR_OFERTA',       'Por Oferta'
        CADENA_FORMACION = 'CADENA_FORMACION', 'Cadena de Formación'
        OTRO         = 'OTRO',         'Otro'
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    nivel = models.CharField(
        max_length=20, choices=Nivel.choices,
        default=Nivel.TECNICO, db_index=True,
    )
    horas_lectivas  = models.PositiveIntegerField()
    horas_practicas = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices,
        default=Estado.ACTIVO, db_index=True,
    )
    trimestres_totales = models.PositiveIntegerField(
        default=6,
        help_text='Total de trimestres antes de etapa productiva.',
    )
    tipo_formacion = models.CharField(
        max_length=20,
        choices=TipoFormacion.choices,
        default=TipoFormacion.POR_OFERTA,
        db_index=True,
    )
    trimestres_cadena = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Trimestres en etapa lectiva para cadena de formación. Menor a trimestres_totales.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name        = 'Programa'
        verbose_name_plural = 'Programas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_nivel_display()})"
    
    def clean(self):
        if self.tipo_formacion == self.TipoFormacion.CADENA_FORMACION:
            if not self.trimestres_cadena:
                raise ValidationError({'trimestres_cadena': 'Requerido para cadena de formación.'})
            if self.trimestres_cadena >= self.trimestres_totales:
                raise ValidationError({'trimestres_cadena': 'Debe ser menor que trimestres_totales.'})
        else:
            # Limpiar el campo si no aplica
            self.trimestres_cadena = None
            
    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)
        
    @property
    def total_horas(self):
        return self.horas_lectivas + self.horas_practicas