from rest_framework import serializers
from competencia.models.competencia_model import Competencia
from competencia.serializers.mixins import DjangoValidationErrorMixin


class CompetenciaTransversalCreateSerializer(DjangoValidationErrorMixin, serializers.ModelSerializer):
    """
    Crea competencias TRANSVERSALES (pertenecen al centro, no a una
    asignatura). El tipo y la asignatura se fuerzan automáticamente.
    """

    class Meta:
        model = Competencia
        fields = [
            'codigo', 'nombre', 'descripcion',
            'es_induccion', 'induccion_activa',
            'horas_trimestre_transversal',
        ]
        extra_kwargs = {
            'horas_trimestre_transversal': {'required': True, 'allow_null': False},
        }

    def validate_codigo(self, value):
        value = value.upper().strip()
        if Competencia.objects.filter(codigo=value).exists():
            raise serializers.ValidationError(
                f'Ya existe una competencia con el código "{value}".'
            )
        return value

    def validate_horas_trimestre_transversal(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Las horas por trimestre deben ser mayores a 0.'
            )
        return value

    def create(self, validated_data):
        validated_data['tipo'] = Competencia.TipoCompetencia.TRANSVERSAL
        validated_data['asignatura'] = None
        return super().create(validated_data)