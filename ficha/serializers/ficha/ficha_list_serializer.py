# ficha/serializers/ficha/ficha_list_serializer.py
from rest_framework import serializers
from ficha.models.ficha_model import Ficha


class FichaListSerializer(serializers.ModelSerializer):
    # FIX: eliminado `qs = Ficha.objects.select_related(...)` a nivel de clase.
    # Ejecutaba una query en la importación del módulo, nunca era usado por el
    # serializer, y podía romper en entornos sin migraciones aplicadas.
    # La optimización de queryset corresponde al ViewSet (get_queryset).

    programa_nombre = serializers.CharField(
        source='version.programa.nombre', read_only=True
    )
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
    jefe_grupo_nombre = serializers.CharField(
        source='jefe_grupo.nombre', read_only=True, default=None
    )

    class Meta:
        model  = Ficha
        fields = [
            'id', 'codigo_ficha',
            'programa_nombre', 'version_numero',
            'jornada', 'jornada_display',
            'etapa', 'etapa_display',
            'trimestre', 'estado',
            'cadena_formacion',
            'numero_estudiantes_estimado',
            'numero_estudiantes_real',
            'jefe_grupo_nombre',
            'fecha_inicio', 'fecha_finalizacion',
        ]