# serializers/resultado_aprendizaje/rap_detail_serializer.py
from rest_framework import serializers
from competencia.models.resultado_aprendizaje_model import ResultadoAprendizaje
from competencia.serializers.competencia.competencia_list_serializer import CompetenciaListSerializer

class RAPDetailSerializer(serializers.ModelSerializer):

    competencia = CompetenciaListSerializer(read_only=True)

    class Meta:
        model = ResultadoAprendizaje
        fields = [
            'id', 'competencia', 'codigo',
            'descripcion', 'criterios_evaluacion',
            'created_at', 'updated_at',
        ]