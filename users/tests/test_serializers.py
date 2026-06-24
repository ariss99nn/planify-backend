from django.test import TestCase, RequestFactory
from unittest.mock import patch
from users.tests.factories import make_user, make_coordinador
from users.models import User
from users.serializers import (
    UserCreateSerializer,
    UserChangeRoleSerializer,
    UsernameChangeSerializer,
    EmailChangeRequestSerializer,
    UserDesactivateSerializer,
)


class UserCreateSerializerTest(TestCase):

    @patch('users.services.email_service.send_mail')
    def test_create_usuario_valido(self, mock_send_mail):
        data = {
            'nombre': 'Juan Test',
            'email': 'juan@test.com',
            'username': 'juantest',
            'rol': User.Rol.ESTUDIANTE,
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertFalse(user.estado)
        self.assertEqual(user.email, 'juan@test.com')

    @patch('users.services.email_service.send_mail')
    def test_passwords_no_coinciden(self, mock_send_mail):
        data = {
            'nombre': 'Juan',
            'email': 'juan2@test.com',
            'username': 'juan2',
            'rol': User.Rol.ESTUDIANTE,
            'password': 'TestPass123!',
            'password2': 'OtraPass123!',
        }
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    @patch('users.services.email_service.send_mail')
    def test_email_duplicado(self, mock_send_mail):
        make_user(email='duplicado@test.com')
        data = {
            'nombre': 'Otro',
            'email': 'duplicado@test.com',
            'username': 'otro',
            'rol': User.Rol.ESTUDIANTE,
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    @patch('users.services.email_service.send_mail')
    def test_email_normalizado_a_lowercase(self, mock_send_mail):
        data = {
            'nombre': 'Ana',
            'email': 'ANA@TEST.COM',
            'username': 'ana',
            'rol': User.Rol.ESTUDIANTE,
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, 'ana@test.com')


class UserChangeRoleSerializerTest(TestCase):

    def _make_request(self, user):
        request = RequestFactory().patch('/')
        request.user = user
        return request

    def test_coordinador_puede_cambiar_rol(self):
        coord = make_coordinador(email='coord@test.com')
        target = make_user(rol=User.Rol.ESTUDIANTE, email='estudiante@test.com')
        serializer = UserChangeRoleSerializer(
            target,
            data={'rol': User.Rol.DOCENTE},
            context={'request': self._make_request(coord)},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_no_puede_cambiar_su_propio_rol(self):
        coord = make_coordinador(email='coord2@test.com')
        serializer = UserChangeRoleSerializer(
            coord,
            data={'rol': User.Rol.ESTUDIANTE},
            context={'request': self._make_request(coord)},
        )
        self.assertFalse(serializer.is_valid())

    def test_no_puede_degradar_ultimo_coordinador(self):
        coord = make_coordinador(email='ultimo_coord@test.com')
        # coord es el único coordinador activo
        serializer = UserChangeRoleSerializer(
            coord,
            data={'rol': User.Rol.DOCENTE},
            context={'request': self._make_request(coord)},
        )
        # Falla porque no puede modificarse a sí mismo
        self.assertFalse(serializer.is_valid())

    def test_docente_no_puede_cambiar_roles(self):
        docente = make_user(rol=User.Rol.DOCENTE, email='doc@test.com')
        target = make_user(rol=User.Rol.ESTUDIANTE, email='est@test.com')
        serializer = UserChangeRoleSerializer(
            target,
            data={'rol': User.Rol.DOCENTE},
            context={'request': self._make_request(docente)},
        )
        self.assertFalse(serializer.is_valid())


class UsernameChangeSerializerTest(TestCase):

    def _make_request(self, user):
        request = RequestFactory().patch('/')
        request.user = user
        return request

    def test_username_disponible(self):
        user = make_user(email='u1@test.com')
        serializer = UsernameChangeSerializer(
            user,
            data={'username': 'nuevo_username'},
            context={'request': self._make_request(user)},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_username_ya_en_uso(self):
        make_user(email='u2@test.com', username='taken_username')
        user = make_user(email='u3@test.com')
        serializer = UsernameChangeSerializer(
            user,
            data={'username': 'taken_username'},
            context={'request': self._make_request(user)},
        )
        self.assertFalse(serializer.is_valid())

    def test_mismo_username_case_insensitive(self):
        make_user(email='u4@test.com', username='ExistingUser')
        user = make_user(email='u5@test.com')
        serializer = UsernameChangeSerializer(
            user,
            data={'username': 'existinguser'},
            context={'request': self._make_request(user)},
        )
        self.assertFalse(serializer.is_valid())


class UserDeactivateSerializerTest(TestCase):

    def test_confirmacion_true(self):
        user = make_user()
        serializer = UserDesactivateSerializer(user, data={'confirmacion': True})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_confirmacion_false_invalida(self):
        user = make_user()
        serializer = UserDesactivateSerializer(user, data={'confirmacion': False})
        self.assertFalse(serializer.is_valid())