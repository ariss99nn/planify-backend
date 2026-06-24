# ficha/models/ficha_model.py
from django.db import models
from django.conf import settings
from programa.models.version_programa_model import VersionPrograma
from django.core.exceptions import ValidationError

class Ficha(models.Model):

    class Jornada(models.TextChoices):
        MANANA = 'MANANA', 'Mañana'
        TARDE = 'TARDE', 'Tarde'
        NOCHE = 'NOCHE', 'Noche'
        MIXTA = 'MIXTA', 'Mixta'

    class Etapa(models.TextChoices):
        LECTIVA = 'LECTIVA', 'Lectiva'
        PRODUCTIVA = 'PRODUCTIVA', 'Productiva'
    class Estado(models.TextChoices):
        ACTIVA    = 'ACTIVA',    'Activa'
        INACTIVA  = 'INACTIVA',  'Inactiva'
        CERRADA   = 'CERRADA',   'Cerrada'  
    codigo_ficha = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
    )
    version = models.ForeignKey(
        VersionPrograma,
        on_delete=models.PROTECT,
        related_name='fichas',
    )
    jornada = models.CharField(
        max_length=10,
        choices=Jornada.choices,
        db_index=True,
    )
    numero_estudiantes_estimado = models.PositiveIntegerField(
        help_text='Cupo estimado al crear la ficha.',
    )
    etapa = models.CharField(
        max_length=15,
        choices=Etapa.choices,
        default=Etapa.LECTIVA,
        db_index=True,
    )
    horas_semanales_objetivo = models.PositiveIntegerField()
    trimestre = models.PositiveIntegerField(
        help_text='Trimestre de formación en curso.',
    )
    estado = models.CharField(
        max_length=10, choices=Estado.choices,
        default=Estado.ACTIVA, db_index=True,
    )
    cadena_formacion = models.BooleanField(
        default=False,
        help_text='Indica si la ficha está en cadena de formación.',
    )
    jefe_grupo = models.ForeignKey(
        'docentes.Docente',
        on_delete=models.PROTECT,
        related_name='fichas_jefe',
        null=True,
        blank=True,
        help_text='Docente responsable del grupo. Debe tener perfil activo.',
    )
    fecha_inicio = models.DateField()
    fecha_finalizacion = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def avanzar_trimestre(self, usuario=None):
        """
        Incrementa el trimestre en 1 dentro de los límites del programa.
        Llama a save() que dispara la señal y crea HistorialEtapa.

        Uso:
            ficha.avanzar_trimestre(usuario=request.user)
        """
        programa = self.version.programa
        if self.cadena_formacion and programa.trimestres_cadena:
            tope = programa.trimestres_cadena
        else:
            tope = programa.trimestres_totales

        if self.trimestre >= tope:
            raise ValidationError(
                f'La ficha ya está en el trimestre máximo ({tope}) '
                f'para este programa.'
            )

        self._cambiado_por = usuario
        self.trimestre += 1
        self.save()

    class Meta:
        verbose_name = 'Ficha'
        verbose_name_plural = 'Fichas'
        ordering = ['-fecha_inicio', 'codigo_ficha']
        indexes = [
            models.Index(fields=['estado', 'etapa']),
            models.Index(fields=['jornada']),
        ]

    def __str__(self):
        return f"Ficha {self.codigo_ficha} — {self.version.programa.nombre}"

    def clean(self):
        if self.fecha_finalizacion and self.fecha_finalizacion < self.fecha_inicio:
            raise ValidationError({'fecha_finalizacion': 'No puede ser anterior a fecha_inicio.'})
        if not self.version_id:
            return 
        programa = self.version.programa
        if self.cadena_formacion:
            if programa.trimestres_cadena is None:
                raise ValidationError({
                    'cadena_formacion': 'El programa no tiene configurados trimestres para cadena de formación.'
                })
            trimestres_max = programa.trimestres_cadena
        else:
            trimestres_max = programa.trimestres_totales

        if self.trimestre > trimestres_max:
            raise ValidationError({'trimestre': f'No puede superar {trimestres_max} para esta modalidad.'})
        if self.jefe_grupo_id and not self.jefe_grupo.estado:
            raise ValidationError({
                'jefe_grupo': 'El docente asignado como jefe de grupo está inactivo.'
            })
    
    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)
        
    @property
    def programa(self):
        return self.version.programa

    @property
    def numero_estudiantes_real(self):
        return self.estudiantes.filter(activo=True).count()

    @property
    def trimestres_restantes(self):
        if self.etapa == self.Etapa.PRODUCTIVA:
            return 0
        programa = self.version.programa
        if self.cadena_formacion and programa.trimestres_cadena:
            total = programa.trimestres_cadena
        else:
            total = programa.trimestres_totales
        return max(0, total - self.trimestre) if total else None