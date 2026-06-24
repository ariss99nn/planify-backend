from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

class Novedad(models.Model):
    """
    Evento operativo que requiere atención de la coordinación.
    Diferencia clave con Alerta: las alertas son técnicas y automáticas
    (colisión de horario, fallo de sistema). Las novedades son operativas
    y requieren una decisión o acción humana.

    Ejemplos:
    - Ficha sin plan aprobado a 5 días del inicio de trimestre.
    - Docente con carga semanal al 95% del máximo.
    - Aula en mantenimiento con bloques activos asignados.
    - Ficha con avance curricular menor al 30% a mitad de trimestre.
    """

    class Tipo(models.TextChoices):
        FICHA_SIN_PLAN         = 'FICHA_SIN_PLAN',         'Ficha sin plan aprobado'
        DOCENTE_SOBRECARGADO   = 'DOCENTE_SOBRECARGADO',   'Docente sobrecargado'
        AULA_CONFLICTO         = 'AULA_CONFLICTO',         'Aula con conflicto'
        AVANCE_BAJO            = 'AVANCE_BAJO',            'Avance curricular bajo'
        ESTUDIANTE_EN_RIESGO   = 'ESTUDIANTE_EN_RIESGO',   'Estudiante en riesgo'
        PLAN_SIN_DOCENTE       = 'PLAN_SIN_DOCENTE',       'Competencia sin docente asignado'
        FICHA_SIN_HORARIO      = 'FICHA_SIN_HORARIO',      'Ficha sin horario generado'
        OTRA                   = 'OTRA',                   'Otra'

    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices,
        db_index=True,
    )
    prioridad = models.PositiveSmallIntegerField(
        choices=[(1, 'Alta'), (2, 'Media'), (3, 'Baja')],
        default=2,
        db_index=True,
    )
    titulo = models.CharField(
        max_length=200,
        help_text='Resumen corto visible en el listado.',
    )
    descripcion = models.TextField(
        help_text='Detalle completo de la novedad.',
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Tipo de entidad afectada.',
    )
    object_id = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='ID de la entidad afectada.',
    )
    entidad_afectada = GenericForeignKey('content_type', 'object_id')

    generada_por_sistema = models.BooleanField(
        default=True,
        help_text='True = generada automáticamente por Celery. False = manual.',
    )
    generada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='novedades_generadas',
        help_text='Solo si generada_por_sistema=False.',
    )

    atendida = models.BooleanField(default=False, db_index=True)
    atendida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='novedades_atendidas',
    )
    fecha_atencion = models.DateTimeField(null=True, blank=True)
    nota_atencion = models.TextField(
        blank=True,
        help_text='Qué se hizo para resolver la novedad.',
    )

    fecha_generacion = models.DateTimeField(auto_now_add=True, db_index=True)
    fecha_expiracion = models.DateTimeField(
        null=True, blank=True,
        help_text='Si se define, la novedad se ignora automáticamente después de esta fecha.',
    )

    class Meta:
        verbose_name        = 'Novedad'
        verbose_name_plural = 'Novedades'
        ordering = ['prioridad', '-fecha_generacion']
        indexes = [
            models.Index(fields=['tipo', 'atendida']),
            models.Index(fields=['prioridad', 'atendida']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"[{self.get_prioridad_display()}] {self.titulo}"

    def marcar_atendida(self, usuario, nota: str = ''):
        if self.atendida:
            return
        from django.utils import timezone
        self.atendida       = True
        self.atendida_por   = usuario
        self.fecha_atencion = timezone.now()
        self.nota_atencion  = nota
        self.save(update_fields=[
            'atendida', 'atendida_por',
            'fecha_atencion', 'nota_atencion',
        ])
        
    def clean(self):
        if not self.generada_por_sistema and not self.generada_por_id:
            raise ValidationError({
                'generada_por': 'Obligatorio si la novedad no es generada por el sistema.'
            })
        if self.generada_por_sistema and self.generada_por_id:
            raise ValidationError({
                'generada_por': 'No aplica para novedades generadas por el sistema.'
            })

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)

    @property
    def esta_vigente(self):
        from django.utils import timezone
        if self.fecha_expiracion:
            return not self.atendida and timezone.now() < self.fecha_expiracion
        return not self.atendida