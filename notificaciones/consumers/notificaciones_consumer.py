# notificaciones/consumers/notificaciones_consumer.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

_MANAGERS_GROUP = 'alertas_managers'


class AlertaConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer para alertas en tiempo real.

    Grupos a los que se suscribe:
      - alertas_user_{pk}   → mensajes personales del usuario autenticado
      - alertas_managers    → solo coordinadores y administrativos
    """

    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        from users.models.user import User

        self.user_group = f'alertas_user_{user.pk}'
        self.is_manager = user.rol in {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO}

        try:
            await self.channel_layer.group_add(self.user_group, self.channel_name)
            if self.is_manager:
                await self.channel_layer.group_add(_MANAGERS_GROUP, self.channel_name)
        except Exception as exc:
            logger.error("Error al unirse al grupo WS: %s", exc)
            await self.close(code=4500)
            return

        await self.accept()
        await self.send(json.dumps({
            'tipo':    'conexion',
            'mensaje': 'Conectado al sistema de notificaciones.',
        }))

    async def disconnect(self, close_code):
        if not hasattr(self, 'user_group'):
            return
        try:
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        except Exception as exc:
            logger.warning("Error al salir del grupo WS %s: %s", self.user_group, exc)

        if getattr(self, 'is_manager', False):
            try:
                await self.channel_layer.group_discard(_MANAGERS_GROUP, self.channel_name)
            except Exception as exc:
                logger.warning("Error al salir del grupo managers: %s", exc)

    async def receive(self, text_data):
        """Solo acepta ping para keepalive. Mensajes malformados se ignoran silenciosamente."""
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, ValueError):
            return
        if data.get('tipo') == 'ping':
            await self.send(json.dumps({'tipo': 'pong'}))

    # ── Handlers del channel layer ──────────────────────────────────────────

    async def alerta_nueva(self, event):
        await self.send(json.dumps({
            'tipo':            'alerta_nueva',
            'id':              event.get('id'),
            'tipo_alerta':     event.get('tipo'),
            'tipo_display':    event.get('tipo_display'),
            'descripcion':     event.get('descripcion'),
            'bloque_origen_id': event.get('bloque_origen_id'),
            'fecha':           event.get('fecha_creacion'),
        }))

    async def alerta_conflicto(self, event):
        """Handler para el tipo 'alerta_conflicto' (grupo managers)."""
        await self.send(json.dumps({
            'tipo':        'conflicto_horario',
            'descripcion': event.get('descripcion'),
            'bloque_id':   event.get('bloque_id'),
            'fecha':       event.get('fecha'),
        }))