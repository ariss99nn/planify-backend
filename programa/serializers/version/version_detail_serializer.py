# programa/serializers/version/version_detail_serializer.py
from rest_framework import serializers
from programa.models.version_programa_model import VersionPrograma
from programa.serializers.programa.programa_list_serializer import ProgramaListSerializer


class VersionDetailSerializer(serializers.ModelSerializer):

    programa = ProgramaListSerializer(read_only=True)
    total_horas = serializers.IntegerField(read_only=True)
    modulos = serializers.SerializerMethodField()

    class Meta:
        model = VersionPrograma
        fields = [
            'id', 'programa', 'numero', 'descripcion',
            'vigente', 'fecha_inicio', 'fecha_fin',
            'total_horas', 'modulos',
            'created_at', 'updated_at',
        ]

    def get_modulos(self, obj):
        from programa.serializers.modulo.modulo_list_serializer import (
            ModuloListSerializer,
        )
        return ModuloListSerializer(
            obj.modulos.all(), many=True
        ).data