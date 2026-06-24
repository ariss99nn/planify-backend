# exportacion/models/exportacion_model.py
from django.db import models
from django.conf import settings


class RegistroExportacion(models.Model):
    """
    Log de auditoría de cada exportación realizada.
    No almacena el archivo — solo el rastro de quién exportó qué y cuándo.
    Obligatorio para cumplimiento institucional sobre datos de estudiantes.
    """

    class TipoExportacion(models.TextChoices):
        FICHAS        = 'FICHAS',        'Fichas'
        ESTUDIANTES   = 'ESTUDIANTES',   'Estudiantes'
        DOCENTES      = 'DOCENTES',      'Docentes'
        HORARIOS      = 'HORARIOS',      'Horarios'
        COMPETENCIAS  = 'COMPETENCIAS',  'Competencias'
        AULAS         = 'AULAS',         'Aulas'
        PLANES        = 'PLANES',        'Planes trimestrales'
        ANALITICA     = 'ANALITICA',     'Analítica'
        COMPLETA      = 'COMPLETA',      'Base de datos completa'

    class Formato(models.TextChoices):
        EXCEL = 'EXCEL', 'Excel (.xlsx)'
        CSV   = 'CSV',   'CSV'
        PDF   = 'PDF',   'PDF'
        JSON  = 'JSON',  'JSON'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='exportaciones',
        help_text='Usuario que realizó la exportación.',
    )
    tipo = models.CharField(
        max_length=15,
        choices=TipoExportacion.choices,
        db_index=True,
    )
    formato = models.CharField(
        max_length=10,
        choices=Formato.choices,
        db_index=True,
    )
    filtros = models.JSONField(
        default=dict,
        help_text='Parámetros aplicados al exportar (fechas, programa, ficha, etc.).',
    )
    registros_exportados = models.PositiveIntegerField(
        default=0,
        help_text='Cantidad de registros incluidos en la exportación.',
    )
    ip_origen = models.GenericIPAddressField(
        null=True, blank=True,
        help_text='IP desde donde se realizó la exportación.',
    )
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name        = 'Registro de exportación'
        verbose_name_plural = 'Registros de exportación'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['usuario', 'fecha']),
            models.Index(fields=['tipo', 'fecha']),
        ]

    def __str__(self):
        return (
            f"{self.usuario} — {self.get_tipo_display()} "
            f"({self.get_formato_display()}) {self.fecha.date()}"
        )