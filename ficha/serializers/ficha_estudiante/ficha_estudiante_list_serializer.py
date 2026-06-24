# ficha/serializers/ficha_estudiante/ficha_estudiante_list_serializer.py
from rest_framework import serializers
from ficha.models.ficha_estudiante_model import FichaEstudiante


class FichaEstudianteListSerializer(serializers.ModelSerializer):

    estudiante_nombre = serializers.CharField(
        source='estudiante.nombre', read_only=True
    )
    estudiante_email = serializers.EmailField(
        source='estudiante.email', read_only=True
    )
    ficha_codigo = serializers.CharField(
        source='ficha.codigo_ficha', read_only=True
    )
    programa_nombre = serializers.CharField(
        source='ficha.version.programa.nombre', read_only=True
    )
    motivo_retiro_display = serializers.CharField(
        source='get_motivo_retiro_display', read_only=True, default=None
    )
    horas_restantes_para_productiva = serializers.SerializerMethodField()

    class Meta:
        model = FichaEstudiante
        fields = [
            'id', 'ficha', 'ficha_codigo', 'programa_nombre',
            'estudiante', 'estudiante_nombre', 'estudiante_email',
            'activo', 'es_cadena',
            'fecha_ingreso', 'fecha_retiro',
            'motivo_retiro', 'motivo_retiro_display',
            'horas_restantes_para_productiva',
        ]

    def get_horas_restantes_para_productiva(self, obj):
        if obj.ficha.etapa == obj.ficha.Etapa.PRODUCTIVA:
            return 0
        trimestres_restantes = obj.ficha.trimestres_restantes
        if trimestres_restantes is None:
            return None
        return trimestres_restantes * obj.ficha.horas_semanales_objetivo * 12