# docentes/serializers/docente_list_serializer.py
from rest_framework import serializers
from docentes.models.docente_model import Docente
from docentes.serializers.docente_base_serializer import BaseDocenteSerializer


class DocenteListSerializer(BaseDocenteSerializer):
    nombre                = serializers.CharField(source='user.nombre_completo', read_only=True)
    email                 = serializers.EmailField(source='user.email', read_only=True)
    avatar                = serializers.ImageField(source='user.imagen', read_only=True)
    horas_asignadas_semana = serializers.FloatField(read_only=True)
    esta_sobrecargado     = serializers.BooleanField(read_only=True)

    class Meta:
        model = Docente
        fields = [
            'id',
            'nombre',
            'email',
            'avatar',                   # foto de perfil del User
            'imagen',                   # foto institucional del Docente
            'especialidad',
            'horas_max_semanales',
            'permite_horas_extra',
            'horas_extra_autorizadas',
            'horas_asignadas_semana',   # computed — carga semanal actual
            'esta_sobrecargado',        # computed — alerta de sobrecarga
            'estado',
        ]