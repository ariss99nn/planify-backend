# serializers/asignatura/asignatura_list_serializer.py
from rest_framework import serializers
from competencia.models.asignatura_model import Asignatura

class AsignaturaListSerializer(serializers.ModelSerializer):

    modulo_nombre = serializers.CharField(
        source='modulo.nombre', read_only=True
    )
    tipo_display = serializers.CharField(
        source='get_tipo_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    total_horas = serializers.IntegerField(read_only=True)
    total_competencias = serializers.SerializerMethodField()

    class Meta:
        model = Asignatura
        fields = [
            'id', 'nombre', 'orden',
            'modulo_nombre', 'tipo', 'tipo_display',
            'estado', 'estado_display',
            'horas_lectivas', 'horas_practicas', 'total_horas',
            'total_competencias',
        ]

    def get_total_competencias(self, obj):
        return obj.competencias.count()