# planificacion/urls/planificacion_urls.py
from django.urls import path

from planificacion.views import (
    BloqueCompetenciaCreateView,
    BloqueCompetenciaListView,
    GenerarHorarioView,
    ItemPlanCreateView,
    ItemPlanListView,
    ItemPlanUpdateView,
    PlanTrimestralCambiarEstadoView,  # CORRECCIÓN: nombre real de la view
    PlanTrimestralCreateView,
    PlanTrimestralDetailView,
    PlanTrimestralListView,
    PlanTrimestralUpdateView,
)

# /api/planes/
plan_urlpatterns = [
    path('',                          PlanTrimestralListView.as_view(),        name='plan-list'),
    path('create/',                   PlanTrimestralCreateView.as_view(),      name='plan-create'),
    path('<int:pk>/',                 PlanTrimestralDetailView.as_view(),      name='plan-detail'),
    path('<int:pk>/update/',          PlanTrimestralUpdateView.as_view(),      name='plan-update'),
    path('<int:pk>/estado/',          PlanTrimestralCambiarEstadoView.as_view(), name='plan-cambiar-estado'),
    path('<int:pk>/generar-horario/', GenerarHorarioView.as_view(),            name='plan-generar-horario'),
]

# /api/items/
item_urlpatterns = [
    path('',                 ItemPlanListView.as_view(),   name='item-list'),
    path('create/',          ItemPlanCreateView.as_view(), name='item-create'),
    path('<int:pk>/update/', ItemPlanUpdateView.as_view(), name='item-update'),
]

# /api/bloques-competencia/
bloque_competencia_urlpatterns = [
    path('',        BloqueCompetenciaListView.as_view(),   name='bc-list'),
    path('create/', BloqueCompetenciaCreateView.as_view(), name='bc-create'),
]