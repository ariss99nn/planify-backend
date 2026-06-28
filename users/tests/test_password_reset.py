"""
users/tests/test_password_reset.py — Refactorizado completo.

CORRECCIONES:
- URLs con prefijo /api/v1/.
- Agregados: test_token_expirado, test_token_ya_usado, test_password_debil.
"""
from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient
from users.tests.factories import make_user, make_password_reset

BASE = '/api/v1'


class PasswordResetFlowTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user(email='reset@test.com')

    @patch('users.services.email_service.send_mail')
    def test_solicitar_reset_email_valido(self, mock_mail):
        r = self.client.post(
            f'{BASE}/auth/password-reset/request/', {'email': 'reset@test.com'}, format='json'
        )
        self.assertEqual(r.status_code, 200)
        mock_mail.assert_called_once()

    @patch('users.services.email_service.send_mail')
    def test_solicitar_reset_email_inexistente_mismo_status(self, mock_mail):
        """Por seguridad no se revela si el email existe."""
        r = self.client.post(
            f'{BASE}/auth/password-reset/request/', {'email': 'noexiste@test.com'}, format='json'
        )
        self.assertEqual(r.status_code, 200)

    @patch('users.services.email_service.send_mail')
    def test_confirmar_reset_token_valido(self, _):
        reset = make_password_reset(self.user)
        r = self.client.post(f'{BASE}/auth/password-reset/confirm/', {
            'token': str(reset.token), 'code': reset.code,
            'new_password': 'NuevoPass123!', 'new_password2': 'NuevoPass123!',
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NuevoPass123!'))

    @patch('users.services.email_service.send_mail')
    def test_confirmar_reset_token_expirado(self, _):
        reset = make_password_reset(self.user, expired=True)
        r = self.client.post(f'{BASE}/auth/password-reset/confirm/', {
            'token': str(reset.token), 'code': reset.code,
            'new_password': 'NuevoPass123!', 'new_password2': 'NuevoPass123!',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    @patch('users.services.email_service.send_mail')
    def test_confirmar_reset_token_ya_usado(self, _):
        reset = make_password_reset(self.user, used=True)
        r = self.client.post(f'{BASE}/auth/password-reset/confirm/', {
            'token': str(reset.token), 'code': reset.code,
            'new_password': 'NuevoPass123!', 'new_password2': 'NuevoPass123!',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    @patch('users.services.email_service.send_mail')
    def test_confirmar_reset_password_debil(self, _):
        reset = make_password_reset(self.user)
        r = self.client.post(f'{BASE}/auth/password-reset/confirm/', {
            'token': str(reset.token), 'code': reset.code,
            'new_password': '123', 'new_password2': '123',
        }, format='json')
        self.assertEqual(r.status_code, 400)
