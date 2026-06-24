# bhorario/urls/bhorario_urls.py
from django.urls import path
from bhorario.views import (
    BloqueHorarioListView,
    BloqueHorarioDetailView,
    BloqueHorarioDeleteView,
    BloqueHorarioCreateView,
    BloqueHorarioUpdateView,
    DisponibilidadView,
    HorarioSemanalView,
)

bhorario_urlpatterns = [
    path('',                 BloqueHorarioListView.as_view(),   name='bhorario-list'),
    path('create/',          BloqueHorarioCreateView.as_view(), name='bhorario-create'),
    path('semanal/',         HorarioSemanalView.as_view(),      name='bhorario-semanal'),
    path('disponibilidad/',  DisponibilidadView.as_view(),      name='bhorario-disponibilidad'),
    path('<int:pk>/',        BloqueHorarioDetailView.as_view(), name='bhorario-detail'),
    path('<int:pk>/update/', BloqueHorarioUpdateView.as_view(), name='bhorario-update'),
    path('<int:pk>/delete/', BloqueHorarioDeleteView.as_view(), name='bhorario-delete'),
]