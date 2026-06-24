import copy
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from aulas.models.bloque_model import Bloque


class BloqueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Bloque
        fields = [
            'nombre', 'pisos', 'capacidad_maxima',
            'estado', 'descripcion', 'imagen',
        ]

    def validate_capacidad_maxima(self, value):
        if value <= 0:
            raise serializers.ValidationError('La capacidad máxima debe ser mayor a 0.')
        return value

    def validate_pisos(self, value):
        if value <= 0:
            raise serializers.ValidationError('El número de pisos debe ser mayor a 0.')
        return value

    def validate(self, attrs):
        temp = copy.copy(self.instance) if self.instance else Bloque()
        for key, val in attrs.items():
            setattr(temp, key, val)

        try:
            temp.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(
                e.message_dict if hasattr(e, 'message_dict')
                else {'non_field_errors': e.messages}
            )
        return attrs