from rest_framework import serializers
from competencia.models.competencia_model import Competencia
from competencia.serializers.mixins import DjangoValidationErrorMixin


class CompetenciaCreateSerializer(DjangoValidationErrorMixin, serializers.ModelSerializer):
    """
    Crea competencias de tipo PRINCIPAL (ligadas a una asignatura).
    Las competencias TRANSVERSALES (tipo, es_induccion,
    horas_trimestre_transversal) no se gestionan desde este endpoint.
    """

    class Meta:
        model = Competencia
        fields = ['asignatura', 'codigo', 'nombre', 'descripcion']
        extra_kwargs = {
            'asignatura': {'required': True, 'allow_null': False},
        }

    def validate_codigo(self, value):
        value = value.upper().strip()
        if Competencia.objects.filter(codigo=value).exists():
            raise serializers.ValidationError(
                f'Ya existe una competencia con el código "{value}".'
            )
        return value