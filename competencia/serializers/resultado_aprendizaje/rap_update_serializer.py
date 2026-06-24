from rest_framework import serializers
from competencia.models.resultado_aprendizaje_model import ResultadoAprendizaje
from competencia.serializers.mixins import DjangoValidationErrorMixin


class RAPUpdateSerializer(DjangoValidationErrorMixin, serializers.ModelSerializer):
    """No permite cambiar competencia ni código."""

    class Meta:
        model = ResultadoAprendizaje
        fields = ['descripcion', 'criterios_evaluacion']