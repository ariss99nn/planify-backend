import copy
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from aulas.models.equipamiento_model import Equipamiento

class EquipamientoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Equipamiento
        fields = [
            'nombre', 'descripcion', 'cantidad',
            'numero_serie', 'fecha_adquisicion',
            'estado', 'imagen',
        ]

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError('La cantidad debe ser mayor a 0.')
        return value

    def validate(self, attrs):
        temp = copy.copy(self.instance) if self.instance else Equipamiento()
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