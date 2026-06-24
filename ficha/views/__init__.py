from ficha.views.ficha import (
    FichaListView, FichaDetailView,
    FichaCreateView, FichaUpdateView, FichaEtapaView,
)
from ficha.views.ficha_estudiante import (
    FichaEstudianteListView,
    FichaEstudianteAddView,
    FichaEstudianteUpdateView,
)
from ficha.views.reasignacion import (
    ReasignacionListView,
    ReasignacionCreateView,
)
from ficha.views.historial import HistorialEtapaListView

__all__ = [
    'FichaListView', 'FichaDetailView',
    'FichaCreateView', 'FichaUpdateView', 'FichaEtapaView',
    'FichaEstudianteListView', 'FichaEstudianteAddView',
    'FichaEstudianteUpdateView',
    'ReasignacionListView', 'ReasignacionCreateView',
    'HistorialEtapaListView',
]