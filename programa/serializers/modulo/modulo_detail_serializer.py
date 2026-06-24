# programa/serializers/modulo/modulo_detail_serializer.py
from rest_framework import serializers
from programa.models.modulo_model import Modulo
from programa.serializers.version.version_list_serializer import VersionListSerializer


class ModuloDetailSerializer(serializers.ModelSerializer):

    version = VersionListSerializer(read_only=True)
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    total_horas = serializers.IntegerField(read_only=True)
    docentes_asignados = serializers.SerializerMethodField()

    class Meta:
        model = Modulo
        fields = [
            'id', 'version', 'nombre', 'descripcion', 'orden',
            'horas_lectivas', 'horas_practicas', 'total_horas',
            'estado', 'estado_display',
            'docentes_asignados',
            'created_at', 'updated_at',
        ]

    def get_docentes_asignados(self, obj):
        from docentes.serializers.docente_habilitacion_serializer import (
            HabilitacionDocenteListSerializer,
        )
        return HabilitacionDocenteListSerializer(
            obj.habilitaciones_docentes.filter(activo=True),
            many=True,
        ).data