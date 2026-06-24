# bhorario/serializers/bloque_horario_list_serializer.py
from rest_framework import serializers
from bhorario.models.bloque_horario_model import BloqueHorario


class BloqueHorarioListSerializer(serializers.ModelSerializer):

    dia_semana_display = serializers.CharField(
        source='get_dia_semana_display', read_only=True,
    )
    jornada_display = serializers.CharField(
        source='get_jornada_display', read_only=True,
    )
    aula_codigo = serializers.CharField(
        source='aula.codigo_aula', read_only=True, default=None,
    )
    docente_nombre = serializers.CharField(
        source='docente.user.nombre', read_only=True, default=None,
    )
    ficha_codigo = serializers.CharField(
        source='ficha.codigo_ficha', read_only=True, default=None,
    )

    class Meta:
        model  = BloqueHorario
        fields = [
            'id', 'dia_semana', 'dia_semana_display',
            'hora_inicio', 'hora_fin',
            'jornada', 'jornada_display',
            'es_recurrente',
            'aula', 'aula_codigo',
            'docente', 'docente_nombre',
            'ficha', 'ficha_codigo',
        ]