from rest_framework import serializers
from aulas.models.aula_model import Aula


class AulaListSerializer(serializers.ModelSerializer):
    bloque_nombre     = serializers.CharField(source='bloque.nombre', read_only=True)
    tipo_aula_display = serializers.CharField(source='get_tipo_aula_display', read_only=True)
    estado_display    = serializers.CharField(source='get_estado_display',    read_only=True)

    class Meta:
        model  = Aula
        fields = [
            'id', 'codigo_aula', 'capacidad',
            'tipo_aula', 'tipo_aula_display',
            'estado', 'estado_display',
            'bloque_nombre', 'piso',
        ]