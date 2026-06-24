from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch
from users.tests.factories import (
    make_coordinador, make_administrativo,
    make_docente, make_estudiante, get_auth_header,
)
from users.models import User


class UserListViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord@test.com')
        self.admin = make_administrativo(email='admin@test.com')
        self.docente = make_docente(email='docente@test.com')
        self.est = make_estudiante(email='est@test.com')

    def test_coordinador_ve_todos(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.get('/api/users/', **headers)
        self.assertEqual(response.status_code, 200)
        emails = [u['email'] for u in response.data['results']]
        self.assertIn('docente@test.com', emails)
        self.assertIn('est@test.com', emails)

    def test_administrativo_ve_todos(self):
        headers = get_auth_header(self.client, self.admin)
        response = self.client.get('/api/users/', **headers)
        self.assertEqual(response.status_code, 200)

    def test_docente_solo_ve_estudiantes(self):
        headers = get_auth_header(self.client, self.docente)
        response = self.client.get('/api/users/', **headers)
        self.assertEqual(response.status_code, 200)
        roles = [u['rol'] for u in response.data['results']]
        self.assertTrue(all(r == User.Rol.ESTUDIANTE for r in roles))
        emails = [u['email'] for u in response.data['results']]
        self.assertNotIn('coord@test.com', emails)
        self.assertNotIn('docente@test.com', emails)

    def test_estudiante_no_accede(self):
        headers = get_auth_header(self.client, self.est)
        response = self.client.get('/api/users/', **headers)
        self.assertEqual(response.status_code, 403)

    def test_sin_autenticacion(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 401)


class UserDetailViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord2@test.com')
        self.docente = make_docente(email='doc2@test.com')
        self.est = make_estudiante(email='est2@test.com')

    def test_coordinador_ve_cualquier_usuario(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.get(f'/api/users/{self.docente.pk}/', **headers)
        self.assertEqual(response.status_code, 200)

    def test_docente_ve_estudiante(self):
        headers = get_auth_header(self.client, self.docente)
        response = self.client.get(f'/api/users/{self.est.pk}/', **headers)
        self.assertEqual(response.status_code, 200)

    def test_docente_no_ve_otro_docente(self):
        otro_docente = make_docente(email='doc3@test.com')
        headers = get_auth_header(self.client, self.docente)
        response = self.client.get(f'/api/users/{otro_docente.pk}/', **headers)
        self.assertEqual(response.status_code, 403)

    def test_docente_no_ve_coordinador(self):
        headers = get_auth_header(self.client, self.docente)
        response = self.client.get(f'/api/users/{self.coord.pk}/', **headers)
        self.assertEqual(response.status_code, 403)

    def test_estudiante_no_accede(self):
        headers = get_auth_header(self.client, self.est)
        response = self.client.get(f'/api/users/{self.coord.pk}/', **headers)
        self.assertEqual(response.status_code, 403)

    def test_usuario_inexistente(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.get('/api/users/99999/', **headers)
        self.assertEqual(response.status_code, 404)


class UserCreateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord3@test.com')
        self.docente = make_docente(email='doc4@test.com')

    @patch('users.serializers.user_create_serializer.send_verification_email')
    def test_coordinador_puede_crear(self, mock_email):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.post('/api/users/create/', {
            'nombre': 'Nuevo Docente',
            'email': 'nuevodoc@test.com',
            'username': 'nuevodoc',
            'rol': User.Rol.DOCENTE,
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }, format='json', **headers)
        self.assertEqual(response.status_code, 201)

    @patch('users.serializers.user_create_serializer.send_verification_email')
    def test_docente_no_puede_crear(self, mock_email):
        headers = get_auth_header(self.client, self.docente)
        response = self.client.post('/api/users/create/', {
            'nombre': 'Intento',
            'email': 'intento@test.com',
            'username': 'intento',
            'rol': User.Rol.ESTUDIANTE,
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }, format='json', **headers)
        self.assertEqual(response.status_code, 403)


class UserUpdateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord4@test.com')
        self.est = make_estudiante(email='est3@test.com')
        self.docente = make_docente(email='doc5@test.com')

    def test_coordinador_puede_actualizar_estado(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            f'/api/users/{self.est.pk}/update/',
            {'estado': False},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)

    def test_coordinador_puede_cambiar_rol(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            f'/api/users/{self.est.pk}/rol/',
            {'rol': User.Rol.DOCENTE},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)

    def test_no_puede_modificarse_a_si_mismo(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            f'/api/users/{self.coord.pk}/update/',
            {'estado': False},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_docente_no_puede_actualizar(self):
        headers = get_auth_header(self.client, self.docente)
        response = self.client.patch(
            f'/api/users/{self.est.pk}/update/',
            {'estado': False},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 403)


class UserDeactivateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord5@test.com')
        self.est = make_estudiante(email='est4@test.com')
        self.docente = make_docente(email='doc6@test.com')

    def test_coordinador_desactiva_usuario(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            f'/api/users/{self.est.pk}/deactivate/',
            {'confirmacion': True},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.est.refresh_from_db()
        self.assertFalse(self.est.estado)

    def test_sin_confirmacion_falla(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            f'/api/users/{self.est.pk}/deactivate/',
            {'confirmacion': False},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_no_puede_desactivarse_a_si_mismo(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            f'/api/users/{self.coord.pk}/deactivate/',
            {'confirmacion': True},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_docente_no_puede_desactivar(self):
        headers = get_auth_header(self.client, self.docente)
        response = self.client.patch(
            f'/api/users/{self.est.pk}/deactivate/',
            {'confirmacion': True},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 403)