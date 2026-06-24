from rest_framework import serializers
from competencia.models.competencia_model import Competencia


class CompetenciaListSerializer(serializers.ModelSerializer):

    asignatura_nombre = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    total_resultados = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id', 'codigo', 'nombre',
            'tipo', 'tipo_display', 'es_induccion',
            'asignatura', 'asignatura_nombre',
            'total_resultados',
        ]

    def get_asignatura_nombre(self, obj):
        return obj.asignatura.nombre if obj.asignatura_id else None

    def get_total_resultados(self, obj):
        return obj.resultados.count()