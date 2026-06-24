# alertas/serializers/alerta_update_serializer.py
from rest_framework import serializers
from django.utils import timezone
from alertas.models.alerta_model import Alerta


class AlertaUpdateSerializer(serializers.ModelSerializer):
    """
    Permite cambiar estado de la alerta.
    Al marcar como LEIDA registra fecha_lectura automáticamente.
    Solo expone 'estado' — formato_alerta no es editable por el usuario.
    """

    class Meta:
        model  = Alerta
        fields = ['estado']

    def update(self, instance, validated_data):
        nuevo_estado = validated_data.get('estado', instance.estado)
        if (
            nuevo_estado == Alerta.EstadoAlerta.LEIDA
            and instance.estado != Alerta.EstadoAlerta.LEIDA
        ):
            validated_data['fecha_lectura'] = timezone.now()
        return super().update(instance, validated_data)