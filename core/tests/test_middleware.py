from unittest.mock import patch, MagicMock, AsyncMock
from django.test import TestCase, RequestFactory, override_settings
from django.http import HttpResponse

from core.middleware.rate_limit_middleware import RolBasedRateLimitMiddleware, _get_client_ip
from core.middleware.cache_headers_middleware import ETagMiddleware
from users.tests.factories import make_docente, make_coordinador


# ─────────────────────────────────────────────────────────────────────────────
# RolBasedRateLimitMiddleware
# ─────────────────────────────────────────────────────────────────────────────

class RateLimitMiddlewareTest(TestCase):
    """Verifica rate limiting por rol y por IP."""

    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda r: HttpResponse('ok')
        self.middleware  = RolBasedRateLimitMiddleware(self.get_response)
        self.docente = make_docente(email_verificado=True)

    @override_settings(CACHES={
        'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}
    })
    def test_primer_request_no_bloqueado(self):
        """El primer request nunca debe ser bloqueado."""
        from django.core.cache import cache
        cache.clear()
        request = self.factory.get('/api/v1/users/')
        request.user = self.docente
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(CACHES={
        'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}
    })
    def test_superar_limite_retorna_429(self):
        """Superar el límite debe retornar 429."""
        from django.core.cache import cache
        cache.clear()

        # Simular que el contador ya está en el límite
        ip = '127.0.0.1'
        rol = self.docente.rol
        limit = 100  # límite para DOCENTE
        cache.set(f'rl:{rol}:{ip}', limit, 60)

        request = self.factory.get('/api/v1/users/')
        request.META['REMOTE_ADDR'] = ip
        request.user = self.docente

        response = self.middleware(request)
        self.assertEqual(response.status_code, 429)

    @override_settings(CACHES={
        'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}
    })
    def test_anonimo_tiene_limite_menor(self):
        """Usuario anónimo tiene límite de 30 req/min."""
        from django.core.cache import cache
        from django.contrib.auth.models import AnonymousUser
        cache.clear()

        ip = '10.0.0.1'
        cache.set(f'rl:anonymous:{ip}', 30, 60)

        request = self.factory.get('/api/v1/users/')
        request.META['REMOTE_ADDR'] = ip
        request.user = AnonymousUser()

        response = self.middleware(request)
        self.assertEqual(response.status_code, 429)

    def test_get_client_ip_sin_proxy(self):
        """Sin proxy, _get_client_ip devuelve REMOTE_ADDR."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.10'
        self.assertEqual(_get_client_ip(request), '192.168.1.10')

    def test_get_client_ip_con_x_forwarded_for(self):
        """Con proxy, _get_client_ip lee la primera IP de X-Forwarded-For."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 10.0.0.1, 172.16.0.1'
        request.META['REMOTE_ADDR'] = '10.0.0.1'  # IP del proxy
        self.assertEqual(_get_client_ip(request), '203.0.113.1')

    def test_get_client_ip_xff_unico_valor(self):
        """X-Forwarded-For con un solo valor retorna ese valor."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.50'
        self.assertEqual(_get_client_ip(request), '203.0.113.50')


# ─────────────────────────────────────────────────────────────────────────────
# ETagMiddleware
# ─────────────────────────────────────────────────────────────────────────────

class ETagMiddlewareTest(TestCase):
    """Verifica generación de ETag y respuesta 304."""

    def setUp(self):
        self.factory = RequestFactory()

        def _get_response(request):
            resp = HttpResponse('{"data": "test"}', content_type='application/json')
            return resp

        self.middleware = ETagMiddleware(_get_response)

    def test_get_request_recibe_etag_header(self):
        """Respuestas GET 200 deben incluir ETag."""
        request = self.factory.get('/api/v1/users/')
        response = self.middleware(request)
        self.assertIn('ETag', response)

    def test_post_request_no_recibe_etag(self):
        """Peticiones POST no deben recibir ETag."""
        request = self.factory.post('/api/v1/users/', data={})
        response = self.middleware(request)
        self.assertNotIn('ETag', response)

    def test_if_none_match_igual_devuelve_304(self):
        """Si If-None-Match coincide con el ETag generado, retorna 304."""
        request = self.factory.get('/api/v1/users/')
        # Primera petición: obtener ETag
        first_response  = self.middleware(request)
        etag = first_response.get('ETag')
        self.assertIsNotNone(etag)

        # Segunda petición: enviar ETag en If-None-Match
        request2 = self.factory.get('/api/v1/users/')
        request2.META['HTTP_IF_NONE_MATCH'] = etag
        second_response = self.middleware(request2)
        self.assertEqual(second_response.status_code, 304)

    def test_if_none_match_diferente_devuelve_200(self):
        """Si If-None-Match es diferente, retorna 200 normalmente."""
        request = self.factory.get('/api/v1/users/')
        request.META['HTTP_IF_NONE_MATCH'] = '"etag_diferente_12345"'
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_last_modified_genera_etag_semantico(self):
        """Si la respuesta incluye Last-Modified, ETag se genera desde ese header."""
        from datetime import datetime, timezone
        from django.utils.http import http_date

        def _response_con_last_modified(request):
            resp = HttpResponse('{}', content_type='application/json')
            resp['Last-Modified'] = http_date(1000000)
            return resp

        middleware = ETagMiddleware(_response_con_last_modified)
        request = self.factory.get('/api/')
        response = middleware(request)
        self.assertIn('ETag', response)
        # El ETag debe ser distinto para Last-Modified distintos
        etag1 = response['ETag']

        def _response_con_otro_lm(request):
            resp = HttpResponse('{}', content_type='application/json')
            resp['Last-Modified'] = http_date(2000000)
            return resp

        middleware2 = ETagMiddleware(_response_con_otro_lm)
        response2 = middleware2(request)
        self.assertNotEqual(etag1, response2['ETag'])


# ─────────────────────────────────────────────────────────────────────────────
# TokenAuthMiddleware (WebSocket)
# ─────────────────────────────────────────────────────────────────────────────

class TokenAuthMiddlewareTest(TestCase):
    """Verifica la autenticación JWT para WebSocket vía query param."""

    def setUp(self):
        self.user = make_docente(email_verificado=True)

    def _get_valid_token(self):
        from rest_framework_simplejwt.tokens import AccessToken
        return str(AccessToken.for_user(self.user))

    @staticmethod
    def _build_scope(query_string: bytes = b''):
        return {'type': 'websocket', 'query_string': query_string}

    def test_token_valido_autentica_usuario(self):
        """Token JWT válido en query param debe autenticar al usuario correcto."""
        from asgiref.sync import async_to_sync
        from notificaciones.middleware.notificaciones_middleware import TokenAuthMiddleware

        token = self._get_valid_token()
        scope = self._build_scope(f'token={token}'.encode())

        received_scope = {}

        async def inner(scope, receive, send):
            received_scope.update(scope)

        middleware = TokenAuthMiddleware(inner)
        async_to_sync(middleware)(scope, None, None)

        self.assertTrue(received_scope['user'].is_authenticated)
        self.assertEqual(received_scope['user'].pk, self.user.pk)

    def test_sin_token_retorna_anonymous(self):
        """Sin token en query_string, scope['user'] debe ser AnonymousUser."""
        from asgiref.sync import async_to_sync
        from notificaciones.middleware.notificaciones_middleware import TokenAuthMiddleware
        from django.contrib.auth.models import AnonymousUser

        scope = self._build_scope(b'')
        received_scope = {}

        async def inner(scope, receive, send):
            received_scope.update(scope)

        middleware = TokenAuthMiddleware(inner)
        async_to_sync(middleware)(scope, None, None)

        self.assertIsInstance(received_scope['user'], AnonymousUser)

    def test_token_invalido_retorna_anonymous(self):
        """Token malformado debe resultar en AnonymousUser, sin excepción."""
        from asgiref.sync import async_to_sync
        from notificaciones.middleware.notificaciones_middleware import TokenAuthMiddleware
        from django.contrib.auth.models import AnonymousUser

        scope = self._build_scope(b'token=este_no_es_un_jwt_valido')
        received_scope = {}

        async def inner(scope, receive, send):
            received_scope.update(scope)

        middleware = TokenAuthMiddleware(inner)
        async_to_sync(middleware)(scope, None, None)

        self.assertIsInstance(received_scope['user'], AnonymousUser)

    def test_token_de_usuario_eliminado_retorna_anonymous(self):
        """Token válido pero usuario eliminado de la BD → AnonymousUser."""
        from asgiref.sync import async_to_sync
        from notificaciones.middleware.notificaciones_middleware import TokenAuthMiddleware
        from django.contrib.auth.models import AnonymousUser

        token = self._get_valid_token()
        self.user.delete()  # Eliminar el usuario

        scope = self._build_scope(f'token={token}'.encode())
        received_scope = {}

        async def inner(scope, receive, send):
            received_scope.update(scope)

        middleware = TokenAuthMiddleware(inner)
        async_to_sync(middleware)(scope, None, None)

        self.assertIsInstance(received_scope['user'], AnonymousUser)
