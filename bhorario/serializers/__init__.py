# bhorario/serializers/__init__.py
from bhorario.serializers.bloque_horario_create_serializer import BloqueHorarioCreateSerializer
from bhorario.serializers.bloque_horario_detail_serializer import BloqueHorarioDetailSerializer
from bhorario.serializers.bloque_horario_list_serializer   import BloqueHorarioListSerializer
from bhorario.serializers.bloque_horario_update_serializer import BloqueHorarioUpdateSerializer

__all__ = [
    'BloqueHorarioCreateSerializer',
    'BloqueHorarioDetailSerializer',
    'BloqueHorarioListSerializer',
    'BloqueHorarioUpdateSerializer',
]