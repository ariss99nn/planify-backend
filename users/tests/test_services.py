from django.test import TestCase
from unittest.mock import patch, MagicMock
from users.tests.factories import make_user, make_verification
from users.services.token_service import generate_numeric_code, generate_uuid_token
from users.services.role_service import sync_user_group
from users.services.email_verification_service import verify_email_code
from users.models import User
import uuid


class TokenServiceTest(TestCase):

    def test_generate_numeric_code_longitud(self):
        code = generate_numeric_code()
        self.assertEqual(len(code), 6)

    def test_generate_numeric_code_solo_digitos(self):
        for _ in range(20):
            code = generate_numeric_code()
            self.assertTrue(code.isdigit())

    def test_generate_uuid_token_es_uuid(self):
        token = generate_uuid_token()
        self.assertIsInstance(token, uuid.UUID)

    def test_generate_uuid_token_unico(self):
        tokens = {generate_uuid_token() for _ in range(100)}
        self.assertEqual(len(tokens), 100)


class RoleServiceTest(TestCase):

    def test_sync_user_group_asigna_grupo(self):
        from django.contrib.auth.models import Group
        Group.objects.get_or_create(name=User.Rol.DOCENTE)
        user = make_user(rol=User.Rol.DOCENTE)
        sync_user_group(user)
        grupos = list(user.groups.values_list('name', flat=True))
        self.assertIn(User.Rol.DOCENTE, grupos)

    def test_sync_user_group_reemplaza_grupo_anterior(self):
        from django.contrib.auth.models import Group
        Group.objects.get_or_create(name=User.Rol.DOCENTE)
        Group.objects.get_or_create(name=User.Rol.ESTUDIANTE)
        user = make_user(rol=User.Rol.DOCENTE)
        sync_user_group(user)
        user.rol = User.Rol.ESTUDIANTE
        user.save()
        sync_user_group(user)
        grupos = list(user.groups.values_list('name', flat=True))
        self.assertNotIn(User.Rol.DOCENTE, grupos)
        self.assertIn(User.Rol.ESTUDIANTE, grupos)

    def test_sync_user_group_grupo_inexistente_no_explota(self):
        user = make_user(rol=User.Rol.COORDINADOR)
        # No crear el grupo — debe loggear y retornar sin error
        try:
            sync_user_group(user)
        except Exception as e:
            self.fail(f'sync_user_group lanzó una excepción inesperada: {e}')


class EmailVerificationServiceTest(TestCase):

    def test_verificacion_exitosa(self):
        user = make_user(estado=False)
        make_verification(user)
        success, msg = verify_email_code(user, '123456')
        self.assertTrue(success)
        user.refresh_from_db()
        self.assertTrue(user.estado)

    def test_codigo_incorrecto(self):
        user = make_user(estado=False)
        make_verification(user)
        success, msg = verify_email_code(user, '000000')
        self.assertFalse(success)

    def test_codigo_expirado(self):
        user = make_user(estado=False)
        make_verification(user, expired=True)
        success, msg = verify_email_code(user, '123456')
        self.assertFalse(success)

    def test_sin_verificacion_activa(self):
        user = make_user(estado=False)
        success, msg = verify_email_code(user, '123456')
        self.assertFalse(success)