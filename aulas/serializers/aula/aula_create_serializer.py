import copy
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from aulas.models.aula_model import Aula


class AulaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Aula
        fields = [
            'codigo_aula', 'capacidad', 'tipo_aula',
            'estado', 'bloque', 'piso',
            'descripcion', 'imagen', 'equipamiento',
        ]

    def validate_codigo_aula(self, value):
        value = value.upper().strip()
        qs = Aula.objects.filter(codigo_aula=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe un aula con este código.')
        return value

    def validate(self, attrs):
        # CORRECCIÓN: usar copy + setattr para respetar datos existentes en update,
        # y capturar únicamente DjangoValidationError (no Exception genérico).
        temp = copy.copy(self.instance) if self.instance else Aula()
        for key, val in attrs.items():
            if key == 'equipamiento':   # M2M — no aplica a clean()
                continue
            setattr(temp, key, val)

        try:
            temp.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(
                e.message_dict if hasattr(e, 'message_dict')
                else {'non_field_errors': e.messages}
            )
        return attrs