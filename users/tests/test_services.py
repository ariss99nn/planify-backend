# users/tests/test_services.py
"""Tests de los servicios de usuario."""
import uuid as _uuid
from django.test import TestCase
from users.tests.factories import make_user, make_verification
from users.services.token_service import generate_numeric_code, generate_uuid_token
from users.services.email_verification_service import verify_email_code
from users.models import User


class TokenServiceTest(TestCase):

    def test_generate_numeric_code_tiene_6_digitos(self):
        code = generate_numeric_code()
        self.assertEqual(len(code), 6)

    def test_generate_numeric_code_solo_digitos(self):
        for _ in range(50):
            code = generate_numeric_code()
            self.assertTrue(code.isdigit(), f'Código no numérico: {code}')

    def test_generate_numeric_code_genera_valores_distintos(self):
        codes = {generate_numeric_code() for _ in range(200)}
        self.assertGreater(len(codes), 1)

    def test_generate_uuid_token_es_uuid(self):
        token = generate_uuid_token()
        self.assertIsInstance(token, _uuid.UUID)

    def test_generate_uuid_token_unicidad(self):
        tokens = {generate_uuid_token() for _ in range(100)}
        self.assertEqual(len(tokens), 100)


class RoleServiceTest(TestCase):

    def test_sync_user_group_asigna_grupo(self):
        from django.contrib.auth.models import Group
        from users.services.role_service import sync_user_group
        Group.objects.get_or_create(name=User.Rol.DOCENTE)
        user = make_user(rol=User.Rol.DOCENTE, email='sync1@test.com')
        sync_user_group(user)
        grupos = list(user.groups.values_list('name', flat=True))
        self.assertIn(User.Rol.DOCENTE, grupos)

    def test_sync_user_group_reemplaza_grupo_anterior(self):
        from django.contrib.auth.models import Group
        from users.services.role_service import sync_user_group
        Group.objects.get_or_create(name=User.Rol.DOCENTE)
        Group.objects.get_or_create(name=User.Rol.ESTUDIANTE)
        user = make_user(rol=User.Rol.DOCENTE, email='sync2@test.com')
        sync_user_group(user)
        user.rol = User.Rol.ESTUDIANTE
        user.save(update_fields=['rol'])
        sync_user_group(user)
        grupos = list(user.groups.values_list('name', flat=True))
        self.assertNotIn(User.Rol.DOCENTE,    grupos)
        self.assertIn(User.Rol.ESTUDIANTE, grupos)

    def test_sync_user_group_grupo_inexistente_en_debug_lanza_error(self):
        """En DEBUG=True, grupo inexistente lanza RuntimeError."""
        from django.test import override_settings
        from users.services.role_service import sync_user_group
        user = make_user(rol=User.Rol.COORDINADOR, email='sync3@test.com')
        # Asegurarse que el grupo no existe
        from django.contrib.auth.models import Group
        Group.objects.filter(name=User.Rol.COORDINADOR).delete()
        with override_settings(DEBUG=True):
            with self.assertRaises(RuntimeError):
                sync_user_group(user)


class EmailVerificationServiceTest(TestCase):

    def test_verificacion_exitosa_activa_usuario(self):
        user = make_user(estado=False, email_verificado=False,
                         email='vs1@test.com')
        make_verification(user)
        success, msg = verify_email_code(user, '123456')
        self.assertTrue(success, msg)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_verificado)

    def test_codigo_incorrecto_retorna_false(self):
        user = make_user(estado=False, email_verificado=False,
                         email='vs2@test.com')
        make_verification(user)
        success, _ = verify_email_code(user, '000000')
        self.assertFalse(success)

    def test_codigo_expirado_retorna_false(self):
        user = make_user(estado=False, email_verificado=False,
                         email='vs3@test.com')
        make_verification(user, expired=True)
        success, _ = verify_email_code(user, '123456')
        self.assertFalse(success)

    def test_sin_verificacion_activa_retorna_false(self):
        user = make_user(estado=False, email_verificado=False,
                         email='vs4@test.com')
        success, _ = verify_email_code(user, '123456')
        self.assertFalse(success)

    def test_codigo_ya_usado_retorna_false(self):
        user = make_user(estado=False, email_verificado=False,
                         email='vs5@test.com')
        make_verification(user, used=True)
        success, _ = verify_email_code(user, '123456')
        self.assertFalse(success)

    def test_no_puede_reusar_codigo_despues_de_verificar(self):
        user = make_user(estado=False, email_verificado=False,
                         email='vs6@test.com')
        make_verification(user)
        verify_email_code(user, '123456')  # primera vez: OK
        success2, _ = verify_email_code(user, '123456')  # segunda vez: fail
        self.assertFalse(success2)