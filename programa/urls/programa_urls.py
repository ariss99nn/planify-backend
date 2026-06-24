# programa/urls.py
from django.urls import path
from programa.views import (
    ProgramaListView, ProgramaDetailView,
    ProgramaCreateView, ProgramaUpdateView,
    VersionListView, VersionDetailView,
    VersionCreateView, VersionUpdateView,
    ModuloListView, ModuloDetailView,
    ModuloCreateView, ModuloUpdateView,
)

programa_urlpatterns = [
    path('',                    ProgramaListView.as_view(),   name='programa-list'),
    path('create/',             ProgramaCreateView.as_view(), name='programa-create'),
    path('<int:pk>/',           ProgramaDetailView.as_view(), name='programa-detail'),
    path('<int:pk>/update/',    ProgramaUpdateView.as_view(), name='programa-update'),
]

version_urlpatterns = [
    path('',                    VersionListView.as_view(),   name='version-list'),
    path('create/',             VersionCreateView.as_view(), name='version-create'),
    path('<int:pk>/',           VersionDetailView.as_view(), name='version-detail'),
    path('<int:pk>/update/',    VersionUpdateView.as_view(), name='version-update'),
]

modulo_urlpatterns = [
    path('',                    ModuloListView.as_view(),   name='modulo-list'),
    path('create/',             ModuloCreateView.as_view(), name='modulo-create'),
    path('<int:pk>/',           ModuloDetailView.as_view(), name='modulo-detail'),
    path('<int:pk>/update/',    ModuloUpdateView.as_view(), name='modulo-update'),
]