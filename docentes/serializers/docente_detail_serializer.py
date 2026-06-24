# docentes/serializers/docente_detail_serializer.py
from rest_framework import serializers
from docentes.models.docente_model import Docente
from docentes.serializers.docente_base_serializer import BaseDocenteSerializer
from users.serializers.user_base_serializer import UserBaseSerializer


class DocenteDetailSerializer(BaseDocenteSerializer):
    """
    Detalle completo: datos del User anidados + todos los campos del Docente
    incluyendo horas extra y propiedades computadas de carga horaria.
    """
    user = UserBaseSerializer(read_only=True)
    horas_max_efectivas   = serializers.IntegerField(read_only=True)
    horas_asignadas_semana = serializers.FloatField(read_only=True)
    esta_sobrecargado     = serializers.BooleanField(read_only=True)

    class Meta:
        model = Docente
        fields = [
            'id',
            'user',
            'especialidad',
            'horas_max_semanales',
            'permite_horas_extra',
            'horas_extra_autorizadas',
            'horas_max_efectivas',        # computed
            'horas_asignadas_semana',     # computed
            'esta_sobrecargado',          # computed
            'estado',
            'imagen',
        ]