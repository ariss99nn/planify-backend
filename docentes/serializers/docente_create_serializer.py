# docentes/serializers/docente_create_serializer.py
from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model
from docentes.models.docente_model import Docente
from docentes.serializers.docente_base_serializer import BaseDocenteSerializer

User = get_user_model()


class DocenteCreateSerializer(BaseDocenteSerializer):

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(rol=User.Rol.DOCENTE, is_active=True),
        source='user',
    )

    class Meta:
        model = Docente
        fields = [
            'user_id',
            'especialidad',
            'horas_max_semanales',
            'estado',
            'permite_horas_extra', 
            'horas_extra_autorizadas',
            'imagen',
        ]

    def validate_user_id(self, user):
        if hasattr(user, 'docente'):
            raise serializers.ValidationError(
                "Este usuario ya tiene un perfil de docente asignado."
            )
        return user