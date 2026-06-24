# analitica/models/analitica_snapshot_model.py
from django.db import models


class AnaliticaSnapshot(models.Model):
    """
    Snapshot diario de métricas del sistema.
    Generado por Celery Beat cada noche.
    El detalle por programa vive en SnapshotPrograma (relación inversa).
    """
    fecha = models.DateField(db_index=True, unique=True)

    fichas_activas    = models.PositiveIntegerField(default=0)
    fichas_lectiva    = models.PositiveIntegerField(default=0)
    fichas_productiva = models.PositiveIntegerField(default=0)

    estudiantes_activos  = models.PositiveIntegerField(default=0)
    deserciones_mes      = models.PositiveIntegerField(default=0)
    graduados_mes        = models.PositiveIntegerField(default=0)
    reasignaciones_mes   = models.PositiveIntegerField(default=0)

    docentes_activos       = models.PositiveIntegerField(default=0)
    docentes_sobrecargados = models.PositiveIntegerField(
        default=0,
        help_text='Docentes que superan su horas_max_efectivas en la semana.',
    )

    aulas_activas       = models.PositiveIntegerField(default=0)
    aulas_mantenimiento = models.PositiveIntegerField(default=0)
    aulas_inactivas     = models.PositiveIntegerField(default=0)

    planes_aprobados  = models.PositiveIntegerField(default=0)
    planes_pendientes = models.PositiveIntegerField(default=0)

    alertas_pendientes     = models.PositiveIntegerField(default=0)
    conflictos_horario_mes = models.PositiveIntegerField(default=0)

    # breakdown_programas ELIMINADO — ahora vive en SnapshotPrograma

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Snapshot de analítica'
        verbose_name_plural = 'Snapshots de analítica'
        ordering      = ['-fecha']
        get_latest_by = 'fecha'

    def __str__(self):
        return f"Snapshot {self.fecha}"