from .aula.aula_create_serializer  import AulaCreateSerializer
from .aula.aula_update_serializer  import AulaUpdateSerializer
from .aula.aula_detail_serializer  import AulaDetailSerializer
from .aula.aula_list_serializer    import AulaListSerializer
from .aula.aula_estado_serializer  import AulaEstadoSerializer

from .bloque.bloque_create_serializer  import BloqueCreateSerializer
from .bloque.bloque_update_serializer  import BloqueUpdateSerializer
from .bloque.bloque_detail_serializer  import BloqueDetailSerializer
from .bloque.bloque_list_serializer    import BloqueListSerializer

from .equipamiento.equipamiento_create_serializer  import EquipamientoCreateSerializer
from .equipamiento.equipamiento_update_serializer  import EquipamientoUpdateSerializer
from .equipamiento.equipamiento_detail_serializer  import EquipamientoDetailSerializer
from .equipamiento.equipamiento_list_serializer    import EquipamientoListSerializer

__all__ = [
    'BloqueListSerializer', 'BloqueDetailSerializer',
    'BloqueCreateSerializer', 'BloqueUpdateSerializer',
    'EquipamientoListSerializer', 'EquipamientoDetailSerializer',
    'EquipamientoCreateSerializer', 'EquipamientoUpdateSerializer',
    'AulaListSerializer', 'AulaDetailSerializer',
    'AulaCreateSerializer', 'AulaUpdateSerializer', 'AulaEstadoSerializer',
]