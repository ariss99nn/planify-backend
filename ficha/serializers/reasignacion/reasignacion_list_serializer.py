# ficha/serializers/reasignacion/reasignacion_list_serializer.py
# FIX: import corregido (eliminado prefijo back.).
from rest_framework import serializers
from ficha.models.ficha_reasignacion_model import ReasignacionFicha


class ReasignacionListSerializer(serializers.ModelSerializer):

    estudiante_nombre      = serializers.CharField(
        source='estudiante.nombre', read_only=True
    )
    ficha_origen_codigo    = serializers.CharField(
        source='ficha_origen.codigo_ficha', read_only=True
    )
    ficha_destino_codigo   = serializers.CharField(
        source='ficha_destino.codigo_ficha', read_only=True
    )
    realizado_por_nombre   = serializers.CharField(
        source='realizado_por.nombre', read_only=True, default=None
    )

    class Meta:
        model  = ReasignacionFicha
        fields = [
            'id', 'estudiante', 'estudiante_nombre',
            'ficha_origen',  'ficha_origen_codigo',
            'ficha_destino', 'ficha_destino_codigo',
            'motivo', 'realizado_por', 'realizado_por_nombre',
            'fecha',
        ]