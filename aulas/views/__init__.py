from .aula.aula_list_view   import AulaListView
from .aula.aula_detail_view import AulaDetailView
from .aula.aula_create_view import AulaCreateView
from .aula.aula_update_view import AulaUpdateView
from .aula.aula_estado_view import AulaEstadoView

from .bloque.bloque_list_view   import BloqueListView
from .bloque.bloque_detail_view import BloqueDetailView
from .bloque.bloque_create_view import BloqueCreateView
from .bloque.bloque_update_view import BloqueUpdateView

from .equipamiento.equipamiento_list_view   import EquipamientoListView
from .equipamiento.equipamiento_detail_view import EquipamientoDetailView
from .equipamiento.equipamiento_create_view import EquipamientoCreateView
from .equipamiento.equipamiento_update_view import EquipamientoUpdateView

__all__ = [
    'BloqueListView', 'BloqueDetailView', 'BloqueCreateView', 'BloqueUpdateView',
    'EquipamientoListView', 'EquipamientoDetailView',
    'EquipamientoCreateView', 'EquipamientoUpdateView',
    'AulaListView', 'AulaDetailView', 'AulaCreateView',
    'AulaUpdateView', 'AulaEstadoView',
]