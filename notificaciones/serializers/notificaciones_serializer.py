# notificaciones/serializers/notificaciones_serializer.py
from rest_framework import serializers
from alertas.models.alerta_model import Alerta


class AlertaWSPayloadSerializer(serializers.ModelSerializer):
    """
    Serializa el payload que se envía por WebSocket al crear una Alerta.
    Uso exclusivo del channel layer — no se expone en ningún endpoint REST.
    """

    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Alerta
        fields = [
            'id',
            'tipo',
            'tipo_display',
            'descripcion',
            'bloque_origen_id',
            'destinatario_id',
            'fecha_creacion',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # ISO 8601 explícito para que JS lo parsee sin ambigüedad
        data['fecha_creacion'] = instance.fecha_creacion.isoformat()
        return data