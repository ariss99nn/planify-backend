# bhorario/serializers/bloque_horario_detail_serializer.py
from rest_framework import serializers
from bhorario.models.bloque_horario_model import BloqueHorario


class BloqueHorarioDetailSerializer(serializers.ModelSerializer):

    dia_semana_display = serializers.CharField(
        source='get_dia_semana_display', read_only=True,
    )
    jornada_display = serializers.CharField(
        source='get_jornada_display', read_only=True,
    )
    aula_codigo = serializers.CharField(
        source='aula.codigo_aula', read_only=True, default=None,
    )
    aula_tipo = serializers.CharField(
        source='aula.get_tipo_aula_display', read_only=True, default=None,
    )
    docente_nombre = serializers.CharField(
        source='docente.user.nombre', read_only=True, default=None,
    )
    docente_email = serializers.EmailField(
        source='docente.user.email', read_only=True, default=None,
    )
    ficha_codigo = serializers.CharField(
        source='ficha.codigo_ficha', read_only=True, default=None,
    )
    ficha_programa = serializers.CharField(
        source='ficha.version.programa.nombre', read_only=True, default=None,
    )
    competencia_nombre = serializers.CharField(
        source='competencia.nombre', read_only=True, default=None,
    )
    alertas_activas = serializers.SerializerMethodField()

    class Meta:
        model  = BloqueHorario
        fields = [
            'id', 'dia_semana', 'dia_semana_display',
            'hora_inicio', 'hora_fin',
            'jornada', 'jornada_display',
            'es_recurrente', 'fecha_especifica',
            'aula', 'aula_codigo', 'aula_tipo',
            'docente', 'docente_nombre', 'docente_email',
            'ficha', 'ficha_codigo', 'ficha_programa',
            'competencia', 'competencia_nombre',
            'alertas_activas',
            'created_at', 'updated_at',
        ]

    def get_alertas_activas(self, obj):
        from alertas.models.alerta_model import Alerta
        return obj.alertas.filter(estado=Alerta.EstadoAlerta.PENDIENTE).count()