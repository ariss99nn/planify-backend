from rest_framework import serializers
from aulas.models.bloque_model import Bloque

class BloqueListSerializer(serializers.ModelSerializer):
    # CORRECCIÓN: se agrega estado_display (faltaba en la versión original).
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model  = Bloque
        fields = ['id', 'nombre', 'pisos', 'capacidad_maxima', 'estado', 'estado_display']