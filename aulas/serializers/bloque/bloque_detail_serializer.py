from rest_framework import serializers
from aulas.models.bloque_model import Bloque


class BloqueDetailSerializer(serializers.ModelSerializer):
    # CORRECCIÓN: se agregan estado y estado_display (faltaban en la versión original).
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

   # se usa el valor anotado; si no, cae a la query (retrocompatible).
    total_aulas = serializers.SerializerMethodField()

    class Meta:
        model  = Bloque
        fields = [
            'id', 'nombre', 'pisos', 'capacidad_maxima',
            'estado', 'estado_display',
            'descripcion', 'imagen', 'total_aulas',
        ]

    def get_total_aulas(self, obj):
        if hasattr(obj, 'total_aulas'):
            return obj.total_aulas
        return obj.aulas.count()