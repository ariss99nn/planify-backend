from rest_framework import serializers
from aulas.models.aula_model import Aula


class AulaEstadoSerializer(serializers.ModelSerializer):
    """
    Endpoint PATCH /aulas/{pk}/estado/ — accesible para DOCENTE, COORDINADOR
    y ADMINISTRATIVO (permiso: CanChangeAulaEstado).
    Restringe la edición solo al campo `estado`; el resto del aula es inmutable
    desde este endpoint.
    """
    class Meta:
        model  = Aula
        fields = ['estado']