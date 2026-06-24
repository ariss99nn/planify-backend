from django.urls import path
from aulas.views import (
    BloqueListView, BloqueDetailView, BloqueCreateView, BloqueUpdateView,
    EquipamientoListView, EquipamientoDetailView,
    EquipamientoCreateView, EquipamientoUpdateView,
    AulaListView, AulaDetailView, AulaCreateView,
    AulaUpdateView, AulaEstadoView,
)

bloque_urlpatterns = [
    path('',                 BloqueListView.as_view(),   name='bloque-list'),
    path('create/',          BloqueCreateView.as_view(), name='bloque-create'),
    path('<int:pk>/',        BloqueDetailView.as_view(), name='bloque-detail'),
    path('<int:pk>/update/', BloqueUpdateView.as_view(), name='bloque-update'),
]

equipamiento_urlpatterns = [
    path('',                 EquipamientoListView.as_view(),   name='equipamiento-list'),
    path('create/',          EquipamientoCreateView.as_view(), name='equipamiento-create'),
    path('<int:pk>/',        EquipamientoDetailView.as_view(), name='equipamiento-detail'),
    path('<int:pk>/update/', EquipamientoUpdateView.as_view(), name='equipamiento-update'),
]

aula_urlpatterns = [
    path('',                  AulaListView.as_view(),   name='aula-list'),
    path('create/',           AulaCreateView.as_view(), name='aula-create'),
    path('<int:pk>/',         AulaDetailView.as_view(), name='aula-detail'),
    path('<int:pk>/update/',  AulaUpdateView.as_view(), name='aula-update'),
    path('<int:pk>/estado/',  AulaEstadoView.as_view(), name='aula-estado'),
]