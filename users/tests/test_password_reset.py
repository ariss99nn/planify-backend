from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch
from users.tests.factories import make_user, make_password_reset
from users.models import PasswordReset


class PasswordResetRequestViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    @patch('users.services.email_service.send_mail')
    def test_request_email_existente(self, mock_send_mail):
        make_user(email='reset@test.com')
        response = self.client.post('/api/auth/password-reset/', {
            'email': 'reset@test.com',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_send_mail.called)

    @patch('users.services.email_service.send_mail')
    def test_request_email_inexistente_respuesta_generica(self, mock_send_mail):
        response = self.client.post('/api/auth/password-reset/', {
            'email': 'noexiste@test.com',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_send_mail.called)

    @patch('users.services.email_service.send_mail')
    def test_tokens_anteriores_se_eliminan(self, mock_send_mail):
        user = make_user(email='reset2@test.com')
        make_password_reset(user)
        self.assertEqual(PasswordReset.objects.filter(user=user).count(), 1)
        self.client.post('/api/auth/password-reset/', {
            'email': 'reset2@test.com',
        }, format='json')
        self.assertEqual(PasswordReset.objects.filter(user=user).count(), 1)


class PasswordResetConfirmViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_confirm_exitoso(self):
        user = make_user(email='confirm@test.com')
        reset = make_password_reset(user)
        response = self.client.post('/api/auth/password-reset/confirm/', {
            'code': reset.code,
            'password': 'NuevaPass123!',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        reset.refresh_from_db()
        self.assertTrue(reset.is_used)

    def test_token_invalido(self):
        response = self.client.post('/api/auth/password-reset/confirm/', {
            'code': '000000',
            'password': 'NuevaPass123!',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_token_expirado(self):
        user = make_user(email='expired@test.com')
        reset = make_password_reset(user, expired=True)
        response = self.client.post('/api/auth/password-reset/confirm/', {
            'code': reset.code,
            'password': 'NuevaPass123!',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_token_ya_usado(self):
        user = make_user(email='used@test.com')
        reset = make_password_reset(user, used=True)
        response = self.client.post('/api/auth/password-reset/confirm/', {
            'code': reset.code,
            'password': 'NuevaPass123!',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_password_muy_simple(self):
        user = make_user(email='simple@test.com')
        reset = make_password_reset(user)
        response = self.client.post('/api/auth/password-reset/confirm/', {
            'code': reset.code,
            'password': '1234',
        }, format='json')
        self.assertEqual(response.status_code, 400)