# docentes/models/docente_model.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from users.validators import validate_imagen

class Docente(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='docente',
        limit_choices_to={'rol': 'DOCENTE'},
    )
    especialidad = models.CharField(max_length=100)
    horas_max_semanales = models.PositiveIntegerField(
        default=40,
        help_text='Máximo de horas semanales regulares. Por norma SENA: 40h.',
    )
    permite_horas_extra = models.BooleanField(
        default=False,
        help_text='Autoriza asignación por encima del máximo semanal regular.',
    )
    horas_extra_autorizadas = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            'Horas adicionales autorizadas sobre el máximo regular. '
            'Solo aplica si permite_horas_extra=True.'
        ),
    )
    estado = models.BooleanField(
        default=True,
        help_text='False = inactivo/retirado.',
    )
    imagen = models.ImageField(
        upload_to='docentes/', null=True, blank=True,
        validators=[validate_imagen],
    )
    
    class Meta:
        verbose_name        = 'Docente'
        verbose_name_plural = 'Docentes'
        ordering = ['user__apellido', 'user__nombre']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['especialidad']),
        ]
        
    def __str__(self):
        return f"{self.user.nombre_completo} -- {self.especialidad}"
    
    def clean(self):
        if self.horas_extra_autorizadas > 0 and not self.permite_horas_extra:
            raise ValidationError({
                'horas_extra_autorizadas': (
                    'No se pueden definir horas extra sin activar permite_horas_extra.'
                )
            })
        if self.permite_horas_extra and self.horas_extra_autorizadas == 0:
            raise ValidationError({
                'horas_extra_autorizadas': (
                    'Debe definir las horas extra si permite_horas_extra está activo.'
                )
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def horas_max_efectivas(self):
        """Techo real de horas semanales considerando extras autorizadas."""
        if self.permite_horas_extra:
            return self.horas_max_semanales + self.horas_extra_autorizadas
        return self.horas_max_semanales

    @property
    def horas_asignadas_semana(self):
        bloques = self.bloques_horario.filter(es_recurrente=True).only('hora_inicio', 'hora_fin')
        total_minutos = sum(
            (b.hora_fin.hour * 60 + b.hora_fin.minute) -
            (b.hora_inicio.hour * 60 + b.hora_inicio.minute)
            for b in bloques
        )
        return round(total_minutos / 60, 1)

    @property
    def esta_sobrecargado(self):
        return self.horas_asignadas_semana > self.horas_max_efectivas

    @property
    def nombre_completo(self):
        return self.user.nombre_completo
    
    @property
    def email(self):
        return self.user.email


