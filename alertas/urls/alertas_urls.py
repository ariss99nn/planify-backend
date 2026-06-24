# alertas/urls/alertas_urls.py
from django.urls import path
from alertas.views import (
    AlertaListView,
    AlertaCreateView,
    AlertaUpdateView,
)

alertas_urlpatterns = [
    path('',                 AlertaListView.as_view(),   name='alerta-list'),
    path('create/',          AlertaCreateView.as_view(), name='alerta-create'),
    path('<int:pk>/update/', AlertaUpdateView.as_view(), name='alerta-update'),
]