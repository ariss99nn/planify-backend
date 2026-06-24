from docentes.views.docente_base_view import DocenteBaseView
from docentes.views.docente_list_view import DocenteListView
from docentes.views.docente_detail_view import DocenteDetailView
from docentes.views.docente_create_view import DocenteCreateView
from docentes.views.docente_update_view import DocenteUpdateView
from docentes.views.docente_deactivate_view import DocenteDeactivateView
from docentes.views.docente_disponibilidad_view import (
    DisponibilidadListCreateView,
    DisponibilidadDetailView,
)

__all__ = [
    'DocenteBaseView',
    'DocenteListView',
    'DocenteDetailView',
    'DocenteCreateView',
    'DocenteUpdateView',
    'DocenteDeactivateView',
    'DisponibilidadListCreateView',
    'DisponibilidadDetailView',
]