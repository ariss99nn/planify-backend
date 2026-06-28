from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from unittest.mock import patch, MagicMock
from users.tests.factories import make_user, make_docente, get_auth_header

BASE = '/api/v1'

class RateLimitMiddlewareTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda r: HttpResponse('ok')
        from core.middleware.rate_limit_middleware import RolBasedRateLimitMiddleware
        self.middleware = RolBasedRateLimitMiddleware(self.get_response)
        self.docente_user = make_docente(email='rl_doc@t.com')

    def test_get_client_ip_sin_proxy(self):
        from core.middleware.rate_limit_middleware import _get_client_ip
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.10'
        self.assertEqual(_get_client_ip(request), '192.168.1.10')

    def test_get_client_ip_con_x_forwarded_for_cadena(self):
        from core.middleware.rate_limit_middleware import _get_client_ip
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 10.0.0.1, 172.16.0.1'
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        self.assertEqual(_get_client_ip(request), '203.0.113.1')

    def test_get_client_ip_xff_valor_unico(self):
        from core.middleware.rate_limit_middleware import _get_client_ip
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.50'
        self.assertEqual(_get_client_ip(request), '203.0.113.50')

    def test_get_client_ip_xff_con_espacios(self):
        from core.middleware.rate_limit_middleware import _get_client_ip
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '  203.0.113.99  , 10.0.0.1'
        self.assertEqual(_get_client_ip(request), '203.0.113.99')

    def test_primer_request_no_bloqueado(self):
        from django.core.cache import cache
        from django.test import override_settings
        cache.clear()
        request = self.factory.get(f'{BASE}/users/')
        request.META['REMOTE_ADDR'] = '1.2.3.4'
        request.user = self.docente_user
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_superar_limite_retorna_429(self):
        from django.core.cache import cache
        cache.clear()
        ip = '5.6.7.8'
        rol = self.docente_user.rol
        limit = 100
        cache.set(f'rl:{rol}:{ip}', limit, 60)

        request = self.factory.get(f'{BASE}/users/')
        request.META['REMOTE_ADDR'] = ip
        request.user = self.docente_user
        response = self.middleware(request)
        self.assertEqual(response.status_code, 429)

    def test_anonimo_tiene_limite_30(self):
        from django.core.cache import cache
        from django.contrib.auth.models import AnonymousUser
        cache.clear()
        ip = '9.10.11.12'
        cache.set(f'rl:anonymous:{ip}', 30, 60)
        request = self.factory.get(f'{BASE}/users/')
        request.META['REMOTE_ADDR'] = ip
        request.user = AnonymousUser()
        response = self.middleware(request)
        self.assertEqual(response.status_code, 429)



class ETagMiddlewareTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        def _get_response(request):
            return HttpResponse('{"data": "test"}', content_type='application/json')

        from core.middleware.cache_headers_middleware import ETagMiddleware
        self.middleware = ETagMiddleware(_get_response)

    def test_get_200_recibe_etag_header(self):
        request = self.factory.get(f'{BASE}/users/')
        response = self.middleware(request)
        self.assertIn('ETag', response)

    def test_etag_es_string_entre_comillas(self):
        request = self.factory.get(f'{BASE}/users/')
        response = self.middleware(request)
        etag = response.get('ETag', '')
        self.assertTrue(etag.startswith('"') and etag.endswith('"'))

    def test_post_no_recibe_etag(self):
        request = self.factory.post(f'{BASE}/users/', data={})
        response = self.middleware(request)
        self.assertNotIn('ETag', response)

    def test_if_none_match_igual_devuelve_304(self):
        request = self.factory.get(f'{BASE}/users/')
        first_response = self.middleware(request)
        etag = first_response.get('ETag')
        self.assertIsNotNone(etag)

        request2 = self.factory.get(f'{BASE}/users/')
        request2.META['HTTP_IF_NONE_MATCH'] = etag
        second_response = self.middleware(request2)
        self.assertEqual(second_response.status_code, 304)

    def test_if_none_match_diferente_devuelve_200(self):
        request = self.factory.get(f'{BASE}/users/')
        request.META['HTTP_IF_NONE_MATCH'] = '"etag_diferente"'
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_last_modified_genera_etag_diferente(self):
        from django.utils.http import http_date

        def _resp_lm1(req):
            r = HttpResponse('{}')
            r['Last-Modified'] = http_date(1000000)
            return r

        def _resp_lm2(req):
            r = HttpResponse('{}')
            r['Last-Modified'] = http_date(2000000)
            return r

        from core.middleware.cache_headers_middleware import ETagMiddleware
        m1 = ETagMiddleware(_resp_lm1)
        m2 = ETagMiddleware(_resp_lm2)
        req = self.factory.get('/')
        r1 = m1(req)
        r2 = m2(req)
        self.assertNotEqual(r1['ETag'], r2['ETag'])

    def test_respuesta_no_200_no_recibe_etag(self):
        def _get_404(req):
            return HttpResponse('not found', status=404)

        from core.middleware.cache_headers_middleware import ETagMiddleware
        middleware = ETagMiddleware(_get_404)
        request = self.factory.get('/')
        response = middleware(request)
        self.assertNotIn('ETag', response)



class TokenAuthMiddlewareTest(TestCase):

    def setUp(self):
        self.user = make_user(email='ws_auth@t.com')

    def _get_valid_token(self):
        from rest_framework_simplejwt.tokens import AccessToken
        return str(AccessToken.for_user(self.user))

    @staticmethod
    def _build_scope(query_string: bytes = b''):
        return {'type': 'websocket', 'query_string': query_string}

    def test_token_valido_autentica_usuario(self):
        from asgiref.sync import async_to_sync
        from notificaciones.middleware.notificaciones_middleware import TokenAuthMiddleware

        token = self._get_valid_token()
        scope = self._build_scope(f'token={token}'.encode())
        received_scope = {}

        async def inner(scope, receive, send):
            received_scope.update(scope)

        async_to_sync(TokenAuthMiddleware(inner))(scope, None, None)
        self.assertTrue(received_scope['user'].is_authenticated)
        self.assertEqual(received_scope['user'].pk, self.user.pk)

    def test_sin_token_retorna_anonymous(self):
        from asgiref.sync import async_to_sync
        from notificaciones.middleware.notificaciones_middleware import TokenAuthMiddleware
        from django.contrib.auth.models import AnonymousUser

        scope = self._build_scope(b'')
        received_scope = {}

        async def inner(scope, receive, send):
            received_scope.update(scope)

        async_to_sync(TokenAuthMiddleware(inner))(scope, None, None)
        self.assertIsInstance(received_scope['user'], AnonymousUser)

    def test_token_invalido_retorna_anonymous(self):
        from asgiref.sync import async_to_sync
        from notificaciones.middleware.notificaciones_middleware import TokenAuthMiddleware
        from django.contrib.auth.models import AnonymousUser

        scope = self._build_scope(b'token=no_es_un_jwt_valido')
        received_scope = {}

        async def inner(scope, receive, send):
            received_scope.update(scope)

        async_to_sync(TokenAuthMiddleware(inner))(scope, None, None)
        self.assertIsInstance(received_scope['user'], AnonymousUser)

    def test_usuario_eliminado_retorna_anonymous(self):
        from asgiref.sync import async_to_sync
        from notificaciones.middleware.notificaciones_middleware import TokenAuthMiddleware
        from django.contrib.auth.models import AnonymousUser

        token = self._get_valid_token()
        self.user.delete()
        scope = self._build_scope(f'token={token}'.encode())
        received_scope = {}

        async def inner(scope, receive, send):
            received_scope.update(scope)

        async_to_sync(TokenAuthMiddleware(inner))(scope, None, None)
        self.assertIsInstance(received_scope['user'], AnonymousUser)


