# alertas/serializers/alerta_list_serializer.py
from rest_framework import serializers
from alertas.models.alerta_model import Alerta

class AlertaListSerializer(serializers.ModelSerializer):

    tipo_display = serializers.CharField(
        source='get_tipo_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    formato_display = serializers.CharField(
        source='get_formato_alerta_display', read_only=True
    )
    destinatario_nombre = serializers.CharField(
        source='destinatario.nombre_completo', read_only=True, default=None
    )

    class Meta:
        model = Alerta
        fields = [
            'id', 'tipo', 'tipo_display',
            'estado', 'estado_display',
            'formato_alerta', 'formato_display',
            'descripcion', 'destinatario', 'destinatario_nombre',
            'bloque_origen',
            'fecha_creacion', 'fecha_lectura',
        ]