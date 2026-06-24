from rest_framework import serializers
from aulas.models.aula_model import Aula
from aulas.serializers.bloque.bloque_list_serializer import BloqueListSerializer
from aulas.serializers.equipamiento.equipamiento_list_serializer import EquipamientoListSerializer


class AulaDetailSerializer(serializers.ModelSerializer):
    bloque            = BloqueListSerializer(read_only=True)
    equipamiento      = EquipamientoListSerializer(many=True, read_only=True)
    tipo_aula_display = serializers.CharField(source='get_tipo_aula_display', read_only=True)
    estado_display    = serializers.CharField(source='get_estado_display',    read_only=True)

    class Meta:
        model  = Aula
        fields = [
            'id', 'codigo_aula', 'capacidad',
            'tipo_aula', 'tipo_aula_display',
            'estado', 'estado_display',
            'bloque', 'piso',
            'descripcion', 'imagen', 'equipamiento',
        ]