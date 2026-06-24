# serializers/asignatura/asignatura_detail_serializer.py
from rest_framework import serializers
from competencia.models.asignatura_model import Asignatura

class AsignaturaDetailSerializer(serializers.ModelSerializer):

    modulo_nombre = serializers.CharField(
        source='modulo.nombre', read_only=True
    )
    tipo_display = serializers.CharField(
        source='get_tipo_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    total_horas = serializers.IntegerField(read_only=True)
    competencias = serializers.SerializerMethodField()
    docentes_asignados = serializers.SerializerMethodField()

    class Meta:
        model = Asignatura
        fields = [
            'id', 'modulo', 'modulo_nombre', 'nombre', 'descripcion', 'orden',
            'tipo', 'tipo_display',
            'horas_lectivas', 'horas_practicas', 'total_horas',
            'estado', 'estado_display',
            'competencias', 'docentes_asignados',
            'created_at', 'updated_at',
        ]

    def get_competencias(self, obj):
        from competencia.serializers.competencia.competencia_list_serializer import (
            CompetenciaListSerializer,
        )
        return CompetenciaListSerializer(
            obj.competencias.all(), many=True
        ).data

    def get_docentes_asignados(self, obj):
        from docentes.serializers.docente_habilitacion_serializer import (
            HabilitacionDocenteListSerializer,
        )
        return HabilitacionDocenteListSerializer(
            obj.habilitaciones_docentes.filter(activo=True),
            many=True,
        ).data