from rest_framework import serializers
from competencia.models.competencia_model import Competencia
from competencia.serializers.mixins import DjangoValidationErrorMixin


class CompetenciaTransversalUpdateSerializer(DjangoValidationErrorMixin, serializers.ModelSerializer):
    """No permite cambiar el tipo, código ni asignatura."""

    class Meta:
        model = Competencia
        fields = [
            'nombre', 'descripcion',
            'es_induccion', 'induccion_activa',
            'horas_trimestre_transversal',
        ]

    def validate_horas_trimestre_transversal(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                'Las horas por trimestre deben ser mayores a 0.'
            )
        return value