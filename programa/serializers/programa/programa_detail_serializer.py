# programa/serializers/programa/programa_detail_serializer.py
from rest_framework import serializers
from programa.models.programa_model import Programa


class ProgramaDetailSerializer(serializers.ModelSerializer):

    nivel_display = serializers.CharField(
        source='get_nivel_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    tipo_formacion_display = serializers.CharField(
        source='get_tipo_formacion_display', read_only=True
    )
    total_horas = serializers.IntegerField(read_only=True)
    versiones = serializers.SerializerMethodField()

    class Meta:
        model = Programa
        fields = [
            'id', 'nombre', 'descripcion',
            'nivel', 'nivel_display',
            'horas_lectivas', 'horas_practicas', 'total_horas',
            'estado', 'estado_display',
            'trimestres_totales', 'tipo_formacion', 'tipo_formacion_display',
            'trimestres_cadena',
            'versiones',
            'created_at', 'updated_at',
        ]

    def get_versiones(self, obj):
        from programa.serializers.version.version_list_serializer import (
            VersionListSerializer,
        )
        return VersionListSerializer(
            obj.versiones.all(), many=True
        ).data