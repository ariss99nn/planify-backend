from rest_framework import serializers
from competencia.models.resultado_aprendizaje_model import ResultadoAprendizaje
from competencia.serializers.mixins import DjangoValidationErrorMixin


class RAPCreateSerializer(DjangoValidationErrorMixin, serializers.ModelSerializer):

    class Meta:
        model = ResultadoAprendizaje
        fields = [
            'competencia', 'codigo',
            'descripcion', 'criterios_evaluacion',
        ]

    def validate_codigo(self, value):
        value = value.upper().strip()
        if ResultadoAprendizaje.objects.filter(codigo=value).exists():
            raise serializers.ValidationError(
                f'Ya existe un resultado con el código "{value}".'
            )
        return value