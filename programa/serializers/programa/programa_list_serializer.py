# programa/serializers/programa/programa_list_serializer.py
from rest_framework import serializers
from programa.models.programa_model import Programa


class ProgramaListSerializer(serializers.ModelSerializer):

    nivel_display = serializers.CharField(
        source='get_nivel_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    tipo_formacion_display = serializers.CharField(
        source='get_tipo_formacion_display', read_only=True
    )
    total_horas = serializers.IntegerField(read_only=True)
    total_versiones = serializers.SerializerMethodField()

    class Meta:
        model = Programa
        fields = [
            'id', 'nombre', 'nivel', 'nivel_display',
            'estado', 'estado_display',
            'tipo_formacion', 'tipo_formacion_display',
            'horas_lectivas', 'horas_practicas', 'total_horas',
            'total_versiones',
        ]

    def get_total_versiones(self, obj):
        return obj.versiones.count()