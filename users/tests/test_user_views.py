# users/tests/test_user_views.py
"""
Tests de las vistas de gestión de usuarios (/api/users/).

CORRECCIONES:
- URL base /api/users/ (sin /v1/).
- UserDesactivateView → body: {confirmacion: true} (no estado: false).
- UserActivateView → body: {confirmacion: true}.
- El queryset de DOCENTE solo incluye ESTUDIANTES — no otros docentes.
- Estudiante no tiene acceso a /api/users/ (queryset vacío).
"""
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User
from users.tests.factories import (
    make_user, make_coordinador, make_docente, make_estudiante,
    make_administrativo, get_auth_header,
)

BASE_USERS = '/api/users'
BASE_AUTH  = '/api/auth'


# ──────────────────────────────────────────────────────────────────────────────
class UserListViewTest(TestCase):

    def setUp(self):
        self.client      = APIClient()
        self.coord       = make_coordinador(email='coord@test.com')
        self.admin       = make_administrativo(email='admin@test.com')
        self.docente     = make_docente(email='docente@test.com')
        self.estudiante  = make_estudiante(email='est@test.com')

    def test_coordinador_lista_todos_los_usuarios(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE_USERS}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('results', r.data)

    def test_administrativo_lista_todos_los_usuarios(self):
        headers = get_auth_header(self.client, self.admin)
        r = self.client.get(f'{BASE_USERS}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_ve_solo_estudiantes(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'{BASE_USERS}/', **headers)
        self.assertEqual(r.status_code, 200)
        roles = [u['rol'] for u in r.data.get('results', [])]
        for rol in roles:
            self.assertEqual(rol, User.Rol.ESTUDIANTE)

    def test_estudiante_recibe_lista_vacia(self):
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'{BASE_USERS}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('count', 0), 0)

    def test_sin_autenticacion_retorna_401(self):
        self.assertEqual(
            self.client.get(f'{BASE_USERS}/').status_code, 401
        )

    def test_respuesta_incluye_paginacion(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE_USERS}/', **headers)
        self.assertIn('count',   r.data)
        self.assertIn('results', r.data)

    def test_respuesta_no_incluye_password(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE_USERS}/', **headers)
        for user in r.data.get('results', []):
            self.assertNotIn('password', user)


# ──────────────────────────────────────────────────────────────────────────────
class UserDetailViewTest(TestCase):

    def setUp(self):
        self.client     = APIClient()
        self.coord      = make_coordinador(email='coord2@test.com')
        self.admin      = make_administrativo(email='admin2@test.com')
        self.docente    = make_docente(email='doc2@test.com')
        self.otro_doc   = make_docente(email='otro2@test.com')
        self.estudiante = make_estudiante(email='est2@test.com')

    def test_coordinador_ve_cualquier_usuario(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE_USERS}/{self.docente.pk}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('email', r.data)

    def test_respuesta_no_incluye_password(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE_USERS}/{self.estudiante.pk}/', **headers)
        self.assertNotIn('password', r.data)

    def test_docente_puede_ver_estudiante(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'{BASE_USERS}/{self.estudiante.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_no_puede_ver_otro_docente(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'{BASE_USERS}/{self.otro_doc.pk}/', **headers)
        self.assertEqual(r.status_code, 404)

    def test_usuario_ve_su_propio_perfil(self):
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'{BASE_USERS}/{self.estudiante.pk}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['email'], self.estudiante.email)

    def test_usuario_inexistente_retorna_404(self):
        headers = get_auth_header(self.client, self.coord)
        self.assertEqual(
            self.client.get(f'{BASE_USERS}/99999/', **headers).status_code, 404
        )

    def test_sin_autenticacion_retorna_401(self):
        self.assertEqual(
            self.client.get(f'{BASE_USERS}/{self.coord.pk}/').status_code, 401
        )


# ──────────────────────────────────────────────────────────────────────────────
class UserCreateViewTest(TestCase):

    def setUp(self):
        self.client  = APIClient()
        self.coord   = make_coordinador(email='coord3@test.com')
        self.docente = make_docente(email='doc3@test.com')

    @patch('users.services.email_service.send_welcome_email')
    def test_coordinador_crea_usuario_retorna_201(self, mock_email):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE_USERS}/', {
            'nombre': 'Nuevo',
            'apellido': 'Docente',
            'email': 'nuevodoc@test.com',
            'rol': User.Rol.DOCENTE,
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    @patch('users.services.email_service.send_welcome_email')
    def test_usuario_creado_por_admin_queda_activo(self, mock_email):
        """Cuando un admin crea un usuario, queda activo y verificado."""
        headers = get_auth_header(self.client, self.coord)
        self.client.post(f'{BASE_USERS}/', {
            'nombre': 'Auto',
            'apellido': 'Activo',
            'email': 'autoactivo@test.com',
            'rol': User.Rol.ESTUDIANTE,
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }, format='json', **headers)
        user = User.objects.get(email='autoactivo@test.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_verificado)

    def test_docente_no_puede_crear_usuarios(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post(f'{BASE_USERS}/', {
            'nombre': 'Intento',
            'apellido': 'Fallido',
            'email': 'intento@test.com',
            'rol': User.Rol.ESTUDIANTE,
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_autenticacion_retorna_401(self):
        r = self.client.post(f'{BASE_USERS}/', {
            'nombre': 'Test',
            'apellido': 'User',
            'email': 'unauth@test.com',
            'rol': User.Rol.ESTUDIANTE,
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }, format='json')
        self.assertEqual(r.status_code, 401)


# ──────────────────────────────────────────────────────────────────────────────
class UserChangeRoleViewTest(TestCase):

    def setUp(self):
        self.client     = APIClient()
        self.coord      = make_coordinador(email='coord4@test.com')
        self.coord2     = make_coordinador(email='coord4b@test.com')
        self.docente    = make_docente(email='doc4@test.com')
        self.estudiante = make_estudiante(email='est4@test.com')

    def test_coordinador_cambia_rol_de_estudiante_a_docente(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE_USERS}/{self.estudiante.pk}/rol/',
            {'rol': User.Rol.DOCENTE},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.estudiante.refresh_from_db()
        self.assertEqual(self.estudiante.rol, User.Rol.DOCENTE)

    def test_no_puede_cambiarse_su_propio_rol(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE_USERS}/{self.coord.pk}/rol/',
            {'rol': User.Rol.DOCENTE},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 403)

    def test_no_puede_bajar_unico_coordinador(self):
        """Si solo hay un coordinador activo, no se puede cambiar su rol."""
        # Desactivar coord2 para que coord sea el único
        self.coord2.is_active = False
        self.coord2.save(update_fields=['is_active'])

        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE_USERS}/{self.coord.pk}/rol/',
            {'rol': User.Rol.DOCENTE},
            format='json', **headers,
        )
        # Es su propio rol → 403 por CanManageUser.has_object_permission
        self.assertEqual(r.status_code, 403)

    def test_docente_no_puede_cambiar_rol(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.patch(
            f'{BASE_USERS}/{self.estudiante.pk}/rol/',
            {'rol': User.Rol.DOCENTE},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 403)


# ──────────────────────────────────────────────────────────────────────────────
class UserDesactivateViewTest(TestCase):

    def setUp(self):
        self.client     = APIClient()
        self.coord      = make_coordinador(email='coord5@test.com')
        self.admin      = make_administrativo(email='admin5@test.com')
        self.estudiante = make_estudiante(email='est5@test.com')
        self.docente    = make_docente(email='doc5@test.com')

    def test_coordinador_desactiva_estudiante(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE_USERS}/{self.estudiante.pk}/deactivate/',
            {'confirmacion': True},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.estudiante.refresh_from_db()
        self.assertFalse(self.estudiante.is_active)

    def test_sin_confirmacion_no_desactiva(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE_USERS}/{self.estudiante.pk}/deactivate/',
            {'confirmacion': False},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 400)
        self.estudiante.refresh_from_db()
        self.assertTrue(self.estudiante.is_active)

    def test_sin_body_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE_USERS}/{self.estudiante.pk}/deactivate/',
            {},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 400)

    def test_no_puede_desactivarse_a_si_mismo(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE_USERS}/{self.coord.pk}/deactivate/',
            {'confirmacion': True},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 403)

    def test_docente_no_puede_desactivar(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.patch(
            f'{BASE_USERS}/{self.estudiante.pk}/deactivate/',
            {'confirmacion': True},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 403)

    def test_sin_autenticacion_retorna_401(self):
        r = self.client.patch(
            f'{BASE_USERS}/{self.estudiante.pk}/deactivate/',
            {'confirmacion': True},
            format='json',
        )
        self.assertEqual(r.status_code, 401)

    def test_usuario_inexistente_retorna_404(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE_USERS}/99999/deactivate/',
            {'confirmacion': True},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 404)


# ──────────────────────────────────────────────────────────────────────────────
class UserActivateViewTest(TestCase):

    def setUp(self):
        self.client     = APIClient()
        self.coord      = make_coordinador(email='coord6@test.com')
        self.docente    = make_docente(email='doc6@test.com')
        # Usuario desactivado para reactivar
        self.inactivo   = make_user(
            email='inactivo2@test.com',
            estado=False,
            email_verificado=False,
        )

    def test_coordinador_reactiva_usuario(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE_USERS}/{self.inactivo.pk}/activate/',
            {'confirmacion': True},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.inactivo.refresh_from_db()
        self.assertTrue(self.inactivo.is_active)

    def test_sin_confirmacion_no_reactiva(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE_USERS}/{self.inactivo.pk}/activate/',
            {'confirmacion': False},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 400)

    def test_docente_no_puede_activar(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.patch(
            f'{BASE_USERS}/{self.inactivo.pk}/activate/',
            {'confirmacion': True},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 403)