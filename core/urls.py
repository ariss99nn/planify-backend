from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from users.urls import auth_urlpatterns, user_urlpatterns
from docentes.urls.docente_urls import docente_urlpatterns
from aulas.urls.aulas_urls import (
    bloque_urlpatterns, 
    equipamiento_urlpatterns, 
    aula_urlpatterns
    )

from programa.urls.programa_urls import (
    programa_urlpatterns,
    version_urlpatterns,
    modulo_urlpatterns,
)

from competencia.urls.competencia_urls import (
    asignatura_urlpatterns,
    competencia_urlpatterns,
    rap_urlpatterns,
)

from ficha.urls.ficha_urls import ficha_urlpatterns

from bhorario.urls.bhorario_urls import bhorario_urlpatterns

from alertas.urls.alertas_urls import alertas_urlpatterns

from reportes.urls.reportes_urls import reportes_urlpatterns

from planificacion.urls.planificacion_urls import (
    plan_urlpatterns,
    item_urlpatterns,
    bloque_competencia_urlpatterns,
)

from analitica.views.dashboard_view import DashboardView
from core.views.sync_view import SyncView
from exportacion.urls.exportacion_urls import exportacion_urlpatterns



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chatbot/', include('chatbot.urls')),

    #====================================================================================
    #========RUTAS DEL MODULO USUARIO====================================================
    #====================================================================================

    path('api/auth/', include((auth_urlpatterns, 'auth'))),
    path('api/users/', include((user_urlpatterns, 'users'))),

    #====================================================================================
    #=======RUTAS DE MODULO DOCENTE======================================================
    #====================================================================================

    path('api/docentes/', include((docente_urlpatterns, 'docentes'))),

    #====================================================================================
    #======RUTAS DE MODULO AULAS=========================================================
    #====================================================================================

    path('api/aulas/',          include((aula_urlpatterns, 'aulas'))),
    path('api/bloques/',        include((bloque_urlpatterns, 'bloques'))),
    path('api/equipamiento/',   include((equipamiento_urlpatterns, 'equipamiento'))),

    #====================================================================================
    #=======RUTAS DEL MODULO PROGRAMA====================================================
    #====================================================================================

    path('api/programas/',        include((programa_urlpatterns, 'programas'))),
    path('api/versiones/',        include((version_urlpatterns, 'versiones'))),
    path('api/modulos/',          include((modulo_urlpatterns, 'modulos'))),

    #=====================================================================================
    #========RUTAS DE MODULO COMPETENCIA==================================================
    #=====================================================================================

    path('api/asignaturas/',          include((asignatura_urlpatterns, 'asignaturas'))),
    path('api/competencias/',         include((competencia_urlpatterns, 'competencias'))),
    path('api/resultados/',           include((rap_urlpatterns, 'resultados'))),

    #======================================================================================
    #========RUTAS DE MODULO FICHA=========================================================
    #======================================================================================

    path('api/fichas/', include((ficha_urlpatterns, 'fichas'))),

    #======================================================================================
    #========RUTAS DE MODULO BLOQUE HORARIO================================================
    #======================================================================================

    path('api/horarios/', include((bhorario_urlpatterns, 'horarios'))),

    #======================================================================================
    #========RUTAS DE MODULO ALERTAS========================================================
    #======================================================================================

    path('api/alertas/',  include((alertas_urlpatterns, 'alertas'))),

    #======================================================================================
    #========RUTAS DE MODULO REPORTES======================================================
    #======================================================================================

    path('api/reportes/', include((reportes_urlpatterns, 'reportes'))),

    #======================================================================================
    #========RUTAS DE MODULO PLANIFICACION=================================================
    #======================================================================================
    
    path('api/planes/',             include((plan_urlpatterns, 'planes'))),
    path('api/items-plan/',         include((item_urlpatterns, 'items-plan'))),
    path('api/bloques-competencia/',include((bloque_competencia_urlpatterns, 'bloques-competencia'))),

    #======================================================================================
    #========RUTAS DE ANALITICA=============================================================
    #======================================================================================

    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),

    #=====================================================================================
    #========RUTAS DE API DOCUMENTACION===================================================
    #=====================================================================================

    path('api/schema/',         SpectacularAPIView.as_view(),                          name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'),     name='swagger-ui'),
    path('api/schema/redoc/',   SpectacularRedocView.as_view(url_name='schema'),       name='redoc'),

    #======================================================================================
    #========RUTAS DE SINCRONIZACION========================================================
    #======================================================================================

    path('api/sync/',    SyncView.as_view(),   name='sync'),
    path('api/exportar/', include((exportacion_urlpatterns, 'exportacion'))),
]

if not settings.USE_S3:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

