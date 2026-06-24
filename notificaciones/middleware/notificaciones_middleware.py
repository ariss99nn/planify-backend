import logging
from urllib.parse import parse_qs
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        qs        = parse_qs(scope.get('query_string', b'').decode())
        token_str = qs.get('token', [None])[0]
        scope['user'] = await self._get_user(token_str)
        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def _get_user(self, token_str):
        from django.contrib.auth.models import AnonymousUser

        if not token_str:
            return AnonymousUser()

        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            data = AccessToken(token_str)
        except (InvalidToken, TokenError) as exc:
            logger.info('Token WebSocket inválido: %s', exc)
            return AnonymousUser()

        try:
            return User.objects.get(pk=data['user_id'])
        except User.DoesNotExist:
            logger.warning(
                'Token WS válido pero user_id=%s no encontrado en BD.',
                data.get('user_id'),
            )
            return AnonymousUser()
