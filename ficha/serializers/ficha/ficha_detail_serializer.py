# ficha/serializers/ficha/ficha_detail_serializer.py
from rest_framework import serializers
from ficha.models.ficha_model import Ficha

class FichaDetailSerializer(serializers.ModelSerializer):

    programa_nombre = serializers.CharField(
        source='version.programa.nombre', read_only=True
    )
    
    programa_nivel = serializers.SerializerMethodField()
    version_numero = serializers.IntegerField(
        source='version.numero', read_only=True
    )
    jornada_display = serializers.CharField(
        source='get_jornada_display', read_only=True
    )
    etapa_display = serializers.CharField(
        source='get_etapa_display', read_only=True
    )
    numero_estudiantes_real = serializers.IntegerField(read_only=True)
    trimestres_restantes = serializers.IntegerField(read_only=True)
    jefe_grupo_nombre = serializers.CharField(
        source='jefe_grupo.nombre', read_only=True, default=None
    )
    jefe_grupo_email = serializers.CharField(
        source='jefe_grupo.email', read_only=True, default=None
    )
    historial_etapas_reciente = serializers.SerializerMethodField()

    class Meta:
        model = Ficha
        fields = [
            'id', 'codigo_ficha',
            'version', 'programa_nombre', 'programa_nivel', 'version_numero',
            'jornada', 'jornada_display',
            'etapa', 'etapa_display',
            'trimestre', 'trimestres_restantes',
            'horas_semanales_objetivo',
            'estado', 'cadena_formacion',
            'numero_estudiantes_estimado',
            'numero_estudiantes_real',
            'jefe_grupo', 'jefe_grupo_nombre', 'jefe_grupo_email',
            'fecha_inicio', 'fecha_finalizacion',
            'historial_etapas_reciente',
            'created_at', 'updated_at',
        ]

    def get_historial_etapas_reciente(self, obj):
        from ficha.serializers.historial_etapa.historial_etapa_list_serializer import (
            HistorialEtapaListSerializer,
        )
        return HistorialEtapaListSerializer(
            obj.historial_etapas.all()[:5], many=True
        ).data
    def get_programa_nivel(self, obj):
        return obj.version.programa.get_nivel_display()