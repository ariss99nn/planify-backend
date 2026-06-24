from rest_framework import serializers
from aulas.models.equipamiento_model import Equipamiento


class EquipamientoListSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model  = Equipamiento
        fields = ['id', 'nombre', 'cantidad', 'estado', 'estado_display']