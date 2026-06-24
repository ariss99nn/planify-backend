from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch
from users.tests.factories import (
    make_user, make_verification, get_auth_header, get_token_for_inactive_user,
)
from users.models import User, EmailVerification


class RegisterViewTest(TestCase):

    @patch('users.services.email_service.send_mail')
    def test_registro_exitoso(self, mock_send_mail):
        client = APIClient()
        response = client.post('/api/auth/register/', {
            'nombre': 'Nuevo Usuario',
            'email': 'nuevo@test.com',
            'username': 'nuevousuario',
            'rol': User.Rol.ESTUDIANTE,
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertFalse(User.objects.get(email='nuevo@test.com').estado)

    @patch('users.services.email_service.send_mail')
    def test_registro_email_duplicado(self, mock_send_mail):
        make_user(email='existe@test.com')
        client = APIClient()
        response = client.post('/api/auth/register/', {
            'nombre': 'Otro',
            'email': 'existe@test.com',
            'username': 'otro',
            'rol': User.Rol.ESTUDIANTE,
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    @patch('users.services.email_service.send_mail')
    def test_registro_passwords_no_coinciden(self, mock_send_mail):
        client = APIClient()
        response = client.post('/api/auth/register/', {
            'nombre': 'Test',
            'email': 'test@test.com',
            'username': 'test',
            'rol': User.Rol.ESTUDIANTE,
            'password': 'TestPass123!',
            'password2': 'Diferente123!',
        }, format='json')
        self.assertEqual(response.status_code, 400)


class LoginViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_exitoso(self):
        make_user(email='login@test.com', estado=True)
        response = self.client.post('/api/auth/login/', {
            'email': 'login@test.com',
            'password': 'TestPass123!',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_cuenta_inactiva(self):
        make_user(email='inactivo@test.com', estado=False)
        response = self.client.post('/api/auth/login/', {
            'email': 'inactivo@test.com',
            'password': 'TestPass123!',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_credenciales_invalidas(self):
        response = self.client.post('/api/auth/login/', {
            'email': 'noexiste@test.com',
            'password': 'WrongPass!',
        }, format='json')
        self.assertEqual(response.status_code, 400)


class VerifyEmailViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_verificacion_exitosa(self):
        # Usuario inactivo — usa token directo, no login
        user = make_user(email='verify@test.com', estado=False)
        make_verification(user)
        headers = get_token_for_inactive_user(user)
        response = self.client.post(
            '/api/auth/verify-email/',
            {'code': '123456'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.estado)

    def test_codigo_incorrecto(self):
        user = make_user(email='verify2@test.com')
        make_verification(user)
        headers = get_auth_header(self.client, user)
        response = self.client.post(
            '/api/auth/verify-email/',
            {'code': '000000'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_sin_autenticacion(self):
        response = self.client.post(
            '/api/auth/verify-email/',
            {'code': '123456'},
            format='json',
        )
        self.assertEqual(response.status_code, 401)


class LogoutViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_logout_exitoso(self):
        user = make_user(email='logout@test.com')
        response = self.client.post('/api/auth/login/', {
            'email': 'logout@test.com',
            'password': 'TestPass123!',
        }, format='json')
        refresh = response.data['refresh']
        access = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        logout_response = self.client.post(
            '/api/auth/logout/',
            {'refresh': refresh},
            format='json',
        )
        self.assertEqual(logout_response.status_code, 200)

    def test_logout_token_invalido(self):
        user = make_user(email='logout2@test.com')
        headers = get_auth_header(self.client, user)
        response = self.client.post(
            '/api/auth/logout/',
            {'refresh': 'tokeninvalido'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_logout_sin_autenticacion(self):
        response = self.client.post(
            '/api/auth/logout/',
            {'refresh': 'algo'},
            format='json',
        )
        self.assertEqual(response.status_code, 401)


class RefreshViewTest(TestCase):

    def test_refresh_exitoso(self):
        client = APIClient()
        user = make_user(email='refresh@test.com')
        login = client.post('/api/auth/login/', {
            'email': 'refresh@test.com',
            'password': 'TestPass123!',
        }, format='json')
        response = client.post('/api/auth/refresh/', {
            'refresh': login.data['refresh'],
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)