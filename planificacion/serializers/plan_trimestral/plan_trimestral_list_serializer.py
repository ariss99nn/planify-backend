# planificacion/serializers/plan_trimestral/plan_trimestral_list_serializer.py
from rest_framework import serializers

from planificacion.models.plan_trimestral_model import PlanTrimestral


class PlanTrimestralListSerializer(serializers.ModelSerializer):

    ficha_codigo = serializers.CharField(
        source='ficha.codigo_ficha', read_only=True
    )
    programa_nombre = serializers.CharField(
        source='ficha.version.programa.nombre', read_only=True
    )
    total_horas_planificadas = serializers.DecimalField(
        max_digits=7, decimal_places=1, read_only=True
    )
    total_horas_ejecutadas = serializers.DecimalField(
        max_digits=7, decimal_places=1, read_only=True
    )
    porcentaje_avance = serializers.FloatField(read_only=True)
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    aprobado_por_nombre = serializers.CharField(
        source='aprobado_por.nombre', read_only=True, default=None
    )

    class Meta:
        model  = PlanTrimestral
        fields = [
            'id', 'ficha', 'ficha_codigo', 'programa_nombre',
            'trimestre', 'fecha_inicio', 'fecha_fin',
            'estado', 'estado_display',
            'aprobado_por_nombre', 'fecha_aprobacion',
            'total_horas_planificadas', 'total_horas_ejecutadas',
            'porcentaje_avance',
        ]