import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.settings_dev')

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()  # ← Django se inicializa aquí primero

from channels.routing import ProtocolTypeRouter, URLRouter
from notificaciones.middleware.notificaciones_middleware import TokenAuthMiddleware
from notificaciones.consumers.notificaciones_routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': TokenAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})