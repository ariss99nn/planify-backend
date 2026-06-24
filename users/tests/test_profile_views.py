from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch
from users.tests.factories import (
    make_user, make_estudiante, make_docente,
    make_email_change, get_auth_header,
)


class ProfileViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_perfil_propio(self):
        user = make_user(email='perfil@test.com')
        headers = get_auth_header(self.client, user)
        response = self.client.get('/api/auth/profile/', **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], user.email)

    def test_patch_perfil_nombre(self):
        user = make_user(email='perfil2@test.com')
        headers = get_auth_header(self.client, user)
        response = self.client.patch(
            '/api/auth/profile/',
            {'nombre': 'Nombre Actualizado'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nombre'], 'Nombre Actualizado')

    def test_perfil_sin_autenticacion(self):
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, 401)

    def test_todos_los_roles_acceden_a_su_perfil(self):
        for factory, email in [
            (make_estudiante, 'est@test.com'),
            (make_docente, 'doc@test.com'),
        ]:
            user = factory(email=email)
            headers = get_auth_header(self.client, user)
            response = self.client.get('/api/auth/profile/', **headers)
            self.assertEqual(response.status_code, 200)


class UsernameChangeViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_cambio_exitoso(self):
        user = make_user(email='uname@test.com')
        headers = get_auth_header(self.client, user)
        response = self.client.patch(
            '/api/auth/profile/username/',
            {'username': 'nuevo_uname'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)

    def test_username_ocupado(self):
        make_user(email='uname2@test.com', username='ocupado')
        user = make_user(email='uname3@test.com')
        headers = get_auth_header(self.client, user)
        response = self.client.patch(
            '/api/auth/profile/username/',
            {'username': 'ocupado'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 400)


class EmailChangeViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    @patch('users.services.email_service.send_mail')
    def test_request_cambio_email(self, mock_send_mail):
        user = make_user(email='emailchange@test.com')
        headers = get_auth_header(self.client, user)
        response = self.client.post(
            '/api/auth/profile/email/',
            {'new_email': 'nuevo@test.com'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)

    @patch('users.services.email_service.send_mail')
    def test_request_email_ya_en_uso(self, mock_send_mail):
        make_user(email='ocupado@test.com')
        user = make_user(email='emailchange2@test.com')
        headers = get_auth_header(self.client, user)
        response = self.client.post(
            '/api/auth/profile/email/',
            {'new_email': 'ocupado@test.com'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_confirm_exitoso(self):
        user = make_user(email='emailconfirm@test.com')
        make_email_change(user, new_email='confirmado@test.com')
        headers = get_auth_header(self.client, user)
        response = self.client.post(
            '/api/auth/profile/email/confirm/',
            {'code': '654321'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.email, 'confirmado@test.com')

    def test_confirm_codigo_incorrecto(self):
        user = make_user(email='emailconfirm2@test.com')
        make_email_change(user)
        headers = get_auth_header(self.client, user)
        response = self.client.post(
            '/api/auth/profile/email/confirm/',
            {'code': '000000'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_confirm_expirado(self):
        user = make_user(email='emailconfirm3@test.com')
        make_email_change(user, expired=True)
        headers = get_auth_header(self.client, user)
        response = self.client.post(
            '/api/auth/profile/email/confirm/',
            {'code': '654321'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 400)