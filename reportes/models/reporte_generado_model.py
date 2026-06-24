# reportes/models.py
from django.db import models
from django.conf import settings


class ReporteGenerado(models.Model):

    class TipoReporte(models.TextChoices):
        FICHAS       = 'FICHAS',       'Fichas'
        DOCENTES     = 'DOCENTES',     'Docentes'
        HORARIOS     = 'HORARIOS',     'Horarios'
        COMPETENCIAS = 'COMPETENCIAS', 'Competencias'
        AULAS        = 'AULAS',        'Aulas'
        ANALITICA    = 'ANALITICA',    'Analítica'
        NOVEDADES    = 'NOVEDADES',    'Novedades'
        PLANES       = 'PLANES',       'Planes' 

    class EstadoReporte(models.TextChoices):
        PENDIENTE  = 'PENDIENTE',  'Pendiente'
        PROCESANDO = 'PROCESANDO', 'Procesando'
        LISTO      = 'LISTO',      'Listo'
        ERROR      = 'ERROR',      'Error'

    tipo = models.CharField(
        max_length=20, choices=TipoReporte.choices, db_index=True,
    )
    estado = models.CharField(
        max_length=15, choices=EstadoReporte.choices,
        default=EstadoReporte.PENDIENTE, db_index=True,
    )
    filtros = models.JSONField(
        default=dict,
        help_text='Filtros aplicados al generar el reporte.',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reportes',
    )
    tarea_id = models.CharField(
        max_length=255, null=True, blank=True,
        help_text='ID de tarea Celery.',
    )
    archivo_pdf = models.FileField(
        upload_to='reportes/pdf/', null=True, blank=True,
    )
    archivo_excel = models.FileField(
        upload_to='reportes/excel/', null=True, blank=True,
    )
    error_mensaje = models.TextField(
        blank=True,
        help_text='Mensaje de error si estado=error.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Reporte generado'
        verbose_name_plural = 'Reportes generados'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.get_tipo_display()} -- "
            f"{self.get_estado_display()} ({self.created_at.date()})"
        )