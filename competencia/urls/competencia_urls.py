from django.urls import path

from competencia.views.asignatura.asignatura_list_view import AsignaturaListView
from competencia.views.asignatura.asignatura_create_view import AsignaturaCreateView
from competencia.views.asignatura.asignatura_detail_view import AsignaturaDetailView
from competencia.views.asignatura.asignatura_update_view import AsignaturaUpdateView
from competencia.views.asignatura.asignatura_delete_view import AsignaturaDeleteView

from competencia.views.competencia.competencia_list_view import CompetenciaListView
from competencia.views.competencia.competencia_create_view import CompetenciaCreateView
from competencia.views.competencia.competencia_transversal_create_view import CompetenciaTransversalCreateView
from competencia.views.competencia.competencia_detail_view import CompetenciaDetailView
from competencia.views.competencia.competencia_update_view import CompetenciaUpdateView
from competencia.views.competencia.competencia_delete_view import CompetenciaDeleteView

from competencia.views.resultado_aprendizaje.rap_list_view import RAPListView
from competencia.views.resultado_aprendizaje.rap_create_view import RAPCreateView
from competencia.views.resultado_aprendizaje.rap_detail_view import RAPDetailView
from competencia.views.resultado_aprendizaje.rap_update_view import RAPUpdateView
from competencia.views.resultado_aprendizaje.rap_delete_view import RAPDeleteView


app_name = 'competencia'

urlpatterns = [
    # Asignaturas
    path('asignaturas/', AsignaturaListView.as_view(), name='asignatura-list'),
    path('asignaturas/crear/', AsignaturaCreateView.as_view(), name='asignatura-create'),
    path('asignaturas/<int:pk>/', AsignaturaDetailView.as_view(), name='asignatura-detail'),
    path('asignaturas/<int:pk>/editar/', AsignaturaUpdateView.as_view(), name='asignatura-update'),
    path('asignaturas/<int:pk>/eliminar/', AsignaturaDeleteView.as_view(), name='asignatura-delete'),

    # Competencias
    path('competencias/', CompetenciaListView.as_view(), name='competencia-list'),
    path('competencias/crear/', CompetenciaCreateView.as_view(), name='competencia-create'),
    path('competencias/transversales/crear/', CompetenciaTransversalCreateView.as_view(), name='competencia-transversal-create'),
    path('competencias/<int:pk>/', CompetenciaDetailView.as_view(), name='competencia-detail'),
    path('competencias/<int:pk>/editar/', CompetenciaUpdateView.as_view(), name='competencia-update'),
    path('competencias/<int:pk>/eliminar/', CompetenciaDeleteView.as_view(), name='competencia-delete'),

    # Resultados de aprendizaje
    path('resultados/', RAPListView.as_view(), name='rap-list'),
    path('resultados/crear/', RAPCreateView.as_view(), name='rap-create'),
    path('resultados/<int:pk>/', RAPDetailView.as_view(), name='rap-detail'),
    path('resultados/<int:pk>/editar/', RAPUpdateView.as_view(), name='rap-update'),
    path('resultados/<int:pk>/eliminar/', RAPDeleteView.as_view(), name='rap-delete'),
]

asignatura_urlpatterns = urlpatterns[:5]
competencia_urlpatterns = urlpatterns[5:11]
rap_urlpatterns = urlpatterns[11:]