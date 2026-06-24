from rest_framework import serializers
from competencia.models.competencia_model import Competencia


class CompetenciaDetailSerializer(serializers.ModelSerializer):

    asignatura_nombre = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    resultados = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id', 'asignatura', 'asignatura_nombre',
            'tipo', 'tipo_display',
            'codigo', 'nombre', 'descripcion',
            'es_induccion', 'induccion_activa',
            'horas_trimestre_transversal',
            'resultados',
            'created_at', 'updated_at',
        ]

    def get_asignatura_nombre(self, obj):
        return obj.asignatura.nombre if obj.asignatura_id else None

    def get_resultados(self, obj):
        from competencia.serializers.resultado_aprendizaje.rap_list_serializer import (
            RAPListSerializer,
        )
        return RAPListSerializer(obj.resultados.all(), many=True).data