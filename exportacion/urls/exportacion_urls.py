# exportacion/urls/exportacion_urls.py
from django.urls import path
from exportacion.views.exportacion_view import ExportarView
from exportacion.views.registro_exportacion_view import RegistroExportacionListView

exportacion_urlpatterns = [
    path("exportar/",          ExportarView.as_view(),              name="exportar"),
    path("exportaciones/log/", RegistroExportacionListView.as_view(), name="exportaciones-log"),
]