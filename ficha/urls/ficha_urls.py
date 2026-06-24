# ficha/urls/ficha_urls.py
from django.urls import path
from ficha.views import (
    FichaListView, FichaDetailView,
    FichaCreateView, FichaUpdateView, FichaEtapaView,
    FichaEstudianteListView, FichaEstudianteAddView,
    FichaEstudianteUpdateView,
    ReasignacionListView, ReasignacionCreateView,
    HistorialEtapaListView,
)

ficha_urlpatterns = [
    path('',                                        FichaListView.as_view(),              name='ficha-list'),
    path('create/',                                 FichaCreateView.as_view(),            name='ficha-create'),
    path('historial/',                              HistorialEtapaListView.as_view(),     name='historial-list'),
    path('reasignaciones/',                         ReasignacionListView.as_view(),       name='reasignacion-list'),
    path('reasignaciones/create/',                  ReasignacionCreateView.as_view(),     name='reasignacion-create'),
    path('<int:pk>/',                               FichaDetailView.as_view(),            name='ficha-detail'),
    path('<int:pk>/update/',                        FichaUpdateView.as_view(),            name='ficha-update'),
    path('<int:pk>/etapa/',                         FichaEtapaView.as_view(),             name='ficha-etapa'),
    path('<int:pk>/estudiantes/',                   FichaEstudianteListView.as_view(),    name='ficha-estudiantes'),
    path('<int:pk>/estudiantes/add/',               FichaEstudianteAddView.as_view(),     name='ficha-estudiantes-add'),
    path('<int:pk>/estudiantes/<int:eid>/',         FichaEstudianteUpdateView.as_view(),  name='ficha-estudiante-update'),
]