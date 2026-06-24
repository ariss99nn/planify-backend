# analitica/serializers/snapshot_serializer.py
from rest_framework import serializers
from analitica.models.analitica_snapshot_model import AnaliticaSnapshot
from analitica.models.snapshot_programa_model import SnapshotPrograma


class SnapshotProgramaSerializer(serializers.ModelSerializer):
    programa_nombre = serializers.CharField(
        source='programa.nombre', read_only=True
    )
    avance_horas_pct = serializers.FloatField(read_only=True)

    class Meta:
        model = SnapshotPrograma
        fields = [
            'id', 'programa', 'programa_nombre',
            'fichas_activas', 'fichas_lectiva', 'fichas_productiva',
            'estudiantes_activos', 'deserciones_mes', 'graduados_mes',
            'avance_curricular_pct', 'horas_planificadas',
            'horas_ejecutadas', 'avance_horas_pct',
        ]


class AnaliticaSnapshotSerializer(serializers.ModelSerializer):
    programas = SnapshotProgramaSerializer(many=True, read_only=True)

    class Meta:
        model = AnaliticaSnapshot
        fields = [
            'id', 'fecha',
            'fichas_activas', 'fichas_lectiva', 'fichas_productiva',
            'estudiantes_activos', 'deserciones_mes',
            'graduados_mes', 'reasignaciones_mes',
            'docentes_activos', 'docentes_sobrecargados',
            'aulas_activas', 'aulas_mantenimiento', 'aulas_inactivas',
            'planes_aprobados', 'planes_pendientes',
            'alertas_pendientes', 'conflictos_horario_mes',
            'programas',
            'created_at',
        ]