# serializers/resultado_aprendizaje/rap_list_serializer.py
from rest_framework import serializers
from competencia.models.resultado_aprendizaje_model import ResultadoAprendizaje

class RAPListSerializer(serializers.ModelSerializer):

    competencia_nombre = serializers.CharField(
        source='competencia.nombre', read_only=True
    )

    class Meta:
        model = ResultadoAprendizaje
        fields = [
            'id', 'codigo', 'descripcion',
            'competencia_nombre',
        ]