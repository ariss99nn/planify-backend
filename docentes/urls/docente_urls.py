# docentes/urls/docente_urls.py
from django.urls import path
from docentes.views.docente_list_view import DocenteListView
from docentes.views.docente_detail_view import DocenteDetailView
from docentes.views.docente_create_view import DocenteCreateView
from docentes.views.docente_update_view import DocenteUpdateView
from docentes.views.docente_deactivate_view import DocenteDeactivateView
from docentes.views.docente_disponibilidad_view import (
    DisponibilidadListCreateView,
    DisponibilidadDetailView,
)
from docentes.views.docente_habilitacion_view import (
    HabilitacionDocenteListCreateView,
    HabilitacionDocenteDetailView,
)

# Montadas bajo /api/docentes/
docente_urlpatterns = [
    # ── Docente CRUD ──────────────────────────────────────────────────────────
    path('',                     DocenteListView.as_view(),       name='docente-list'),
    path('create/',              DocenteCreateView.as_view(),     name='docente-create'),
    path('<int:pk>/',            DocenteDetailView.as_view(),     name='docente-detail'),
    path('<int:pk>/update/',     DocenteUpdateView.as_view(),     name='docente-update'),
    path('<int:pk>/deactivate/', DocenteDeactivateView.as_view(), name='docente-deactivate'),

    # ── Disponibilidad ────────────────────────────────────────────────────────
    # GET  → lista   |   POST → crea
    path(
        '<int:pk>/disponibilidad/',
        DisponibilidadListCreateView.as_view(),
        name='docente-disponibilidad-list-create',
    ),
    # PATCH → edita  |   DELETE → elimina (solo gestión)
    path(
        '<int:pk>/disponibilidad/<int:disp_pk>/',
        DisponibilidadDetailView.as_view(),
        name='docente-disponibilidad-detail',
    ),

    # ── Habilitaciones ────────────────────────────────────────────────────────
    # GET  → lista (con filtros y paginación)  |  POST → crea (solo gestión)
    path(
        'habilitaciones/',
        HabilitacionDocenteListCreateView.as_view(),
        name='habilitacion-list-create',
    ),
    # PATCH → actualiza activo / fecha_hasta / observaciones (solo gestión)
    path(
        'habilitaciones/<int:pk>/',
        HabilitacionDocenteDetailView.as_view(),
        name='habilitacion-detail',
    ),
]