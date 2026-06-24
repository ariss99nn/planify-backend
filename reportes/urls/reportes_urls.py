from django.urls import path
from reportes.views.reporte_solicitar_view import (
    SolicitarReporteView,
    EstadoReporteView,
)
from django.urls import path
from reportes.views.novedades_view import (
    NovedadListView,
    NovedadCreateView,
    NovedadAtenderView,
)

reportes_urlpatterns = [
    path('solicitar/', SolicitarReporteView.as_view(), name='reporte-solicitar'),
    path('<int:pk>/',  EstadoReporteView.as_view(),    name='reporte-estado'),
    path('', NovedadListView.as_view(), name='novedad-list'),
    path('crear/', NovedadCreateView.as_view(), name='novedad-create'),
    path('<int:pk>/atender/', NovedadAtenderView.as_view(), name='novedad-atender'),
]
