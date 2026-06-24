# docentes/serializers/docente_update_serializer.py
from docentes.models.docente_model import Docente
from docentes.serializers.docente_base_serializer import BaseDocenteSerializer

class DocenteUpdateSerializer(BaseDocenteSerializer):
    """
    Actualiza campos del perfil docente.
    user_id no es modificable después de la creación.
    """

    class Meta:
        model = Docente
        fields = [
            'especialidad',
            'horas_max_semanales',
            'estado',
            'imagen',
            'permite_horas_extra', 
            'horas_extra_autorizadas',
        ]