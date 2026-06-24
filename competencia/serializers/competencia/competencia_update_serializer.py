from rest_framework import serializers
from competencia.models.competencia_model import Competencia
from competencia.serializers.mixins import DjangoValidationErrorMixin


class CompetenciaUpdateSerializer(DjangoValidationErrorMixin, serializers.ModelSerializer):
    """No permite cambiar la asignatura, el tipo ni el código."""

    class Meta:
        model = Competencia
        fields = ['nombre', 'descripcion']