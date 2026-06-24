from rest_framework import serializers
from aulas.models.equipamiento_model import Equipamiento


class EquipamientoDetailSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model  = Equipamiento
        fields = [
            'id', 'nombre', 'descripcion', 'cantidad',
            'numero_serie', 'fecha_adquisicion',
            'estado', 'estado_display', 'imagen',
        ]