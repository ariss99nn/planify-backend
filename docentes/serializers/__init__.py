from docentes.serializers.docente_base_serializer import BaseDocenteSerializer
from docentes.serializers.docente_create_serializer import DocenteCreateSerializer
from docentes.serializers.docente_list_serializer import DocenteListSerializer
from docentes.serializers.docente_detail_serializer import DocenteDetailSerializer
from docentes.serializers.docente_update_serializer import DocenteUpdateSerializer
from docentes.serializers.docente_deactivate_serializer import DocenteDeactivateSerializer

__all__ = [
    'BaseDocenteSerializer',
    'DocenteCreateSerializer',
    'DocenteListSerializer',
    'DocenteDetailSerializer',
    'DocenteUpdateSerializer',
    'DocenteDeactivateSerializer',
]