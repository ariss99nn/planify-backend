# notificaciones/consumers/notificaciones_routing.py
from django.urls import path
from notificaciones.consumers.notificaciones_consumer import AlertaConsumer

websocket_urlpatterns = [
    path('ws/alertas/', AlertaConsumer.as_asgi()),
]