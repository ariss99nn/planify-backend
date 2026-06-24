# docentes/serializers/docente_deactivate_serializer.py
from django.db import transaction
from rest_framework import serializers
from docentes.models.docente_model import Docente

class DocenteDeactivateSerializer(serializers.ModelSerializer):
    confirmacion = serializers.BooleanField(write_only=True)
    class Meta:
        model = Docente
        fields = ['confirmacion']
    def validate_confirmacion(self, value):
        if value is not True:
            raise serializers.ValidationError(
                "Debe confirmar la desactivación del docente."
            )
        return value
    @transaction.atomic
    def update(self, instance, validated_data):
        instance.estado = False
        instance.save(update_fields=['estado'])

        instance.user.is_active = False
        instance.user.save(update_fields=['is_active'])

        return instance