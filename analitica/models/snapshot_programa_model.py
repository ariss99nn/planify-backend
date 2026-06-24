# analitica/models/snapshot_programa_model.py
from django.db import models


class SnapshotPrograma(models.Model):
    """
    Detalle por programa dentro de un AnaliticaSnapshot.
    Reemplaza el JSONField breakdown_programas.

    Ventajas sobre JSON:
    - Consultable con ORM: .filter(programa=X).order_by('-snapshot__fecha')
    - Indexable
    - Tipado y validado
    - Permite graficar tendencia por programa en analítica
    """
    snapshot = models.ForeignKey(
        'analitica.AnaliticaSnapshot',
        on_delete=models.CASCADE,
        related_name='programas',
    )
    programa = models.ForeignKey(
        'programa.Programa',
        on_delete=models.PROTECT,
        related_name='snapshots',
    )

    fichas_activas    = models.PositiveIntegerField(default=0)
    fichas_lectiva    = models.PositiveIntegerField(default=0)
    fichas_productiva = models.PositiveIntegerField(default=0)

    estudiantes_activos = models.PositiveIntegerField(default=0)
    deserciones_mes     = models.PositiveIntegerField(default=0)
    graduados_mes       = models.PositiveIntegerField(default=0)

    # Promedio de avance curricular de todas las fichas activas del programa
    avance_curricular_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text='Promedio de porcentaje de avance de las fichas activas.',
    )

    # Horas planificadas vs ejecutadas agregadas del programa en este snapshot
    horas_planificadas = models.PositiveIntegerField(default=0)
    horas_ejecutadas   = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name        = 'Snapshot por programa'
        verbose_name_plural = 'Snapshots por programa'
        unique_together = [('snapshot', 'programa')]
        ordering = ['snapshot', 'programa']
        indexes = [
            models.Index(fields=['programa', 'snapshot']),
        ]

    def __str__(self):
        return f"{self.snapshot.fecha} — {self.programa.nombre}"

    @property
    def avance_horas_pct(self):
        if not self.horas_planificadas:
            return 0
        return round((self.horas_ejecutadas / self.horas_planificadas) * 100, 1)