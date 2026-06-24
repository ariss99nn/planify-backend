from programa.views.programa import (
    ProgramaListView, ProgramaDetailView,
    ProgramaCreateView, ProgramaUpdateView,
)
from programa.views.version import (
    VersionListView, VersionDetailView,
    VersionCreateView, VersionUpdateView,
)
from programa.views.modulo import (
    ModuloListView, ModuloDetailView,
    ModuloCreateView, ModuloUpdateView,
)

__all__ = [
    'ProgramaListView', 'ProgramaDetailView',
    'ProgramaCreateView', 'ProgramaUpdateView',
    'VersionListView', 'VersionDetailView',
    'VersionCreateView', 'VersionUpdateView',
    'ModuloListView', 'ModuloDetailView',
    'ModuloCreateView', 'ModuloUpdateView',
]