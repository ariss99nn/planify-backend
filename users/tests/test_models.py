from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from users.tests.factories import (
    make_user, make_verification, make_password_reset, make_email_change
)
from users.models import User


class UserModelTest(TestCase):

    def test_str(self):
        user = make_user(rol=User.Rol.DOCENTE, email='docente@test.com')
        self.assertIn('DOCENTE', user.__str__().upper() or user.get_rol_display().upper())

    def test_es_solo_lectura_estudiante(self):
        user = make_user(rol=User.Rol.ESTUDIANTE)
        self.assertTrue(user.es_solo_lectura())

    def test_es_solo_lectura_otros_roles(self):
        for rol in [User.Rol.DOCENTE, User.Rol.COORDINADOR, User.Rol.ADMIN]:
            user = make_user(rol=rol)
            self.assertFalse(user.es_solo_lectura())

    def test_metodos_rol(self):
        coord = make_user(rol=User.Rol.COORDINADOR)
        self.assertTrue(coord.es_coordinador())
        self.assertFalse(coord.es_docente())
        self.assertFalse(coord.es_administrativo())

        docente = make_user(rol=User.Rol.DOCENTE)
        self.assertTrue(docente.es_docente())

        admin = make_user(rol=User.Rol.ADMIN)
        self.assertTrue(admin.es_administrativo())

    def test_email_es_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_fecha_modificacion_se_actualiza(self):
        user = make_user()
        original = user.fecha_modificacion
        user.nombre = 'Nuevo nombre'
        user.save(update_fields=['nombre'])
        user.refresh_from_db()
        self.assertGreaterEqual(user.fecha_modificacion, original)


class EmailVerificationModelTest(TestCase):

    def test_is_expired_false_cuando_no_expiro(self):
        user = make_user()
        v = make_verification(user, expired=False)
        self.assertFalse(v.is_expired())

    def test_is_expired_true_cuando_expiro(self):
        user = make_user()
        v = make_verification(user, expired=True)
        self.assertTrue(v.is_expired())

    def test_get_expiration_time_retorna_futuro(self):
        from users.models.email_verification import EmailVerification
        exp = EmailVerification.get_expiration_time()
        self.assertGreater(exp, timezone.now())


class PasswordResetModelTest(TestCase):

    def test_is_expired_false(self):
        user = make_user()
        reset = make_password_reset(user, expired=False)
        self.assertFalse(reset.is_expired())

    def test_is_expired_true(self):
        user = make_user()
        reset = make_password_reset(user, expired=True)
        self.assertTrue(reset.is_expired())

    def test_get_expiration_time_usa_settings(self):
        from users.models.password_reset import PasswordReset
        from django.conf import settings
        exp = PasswordReset.get_expiration_time()
        expected_minutes = getattr(settings, 'PASSWORD_RESET_EXPIRY_MINUTES', 120)
        diff = (exp - timezone.now()).total_seconds() / 60
        self.assertAlmostEqual(diff, expected_minutes, delta=1)


class EmailChangeRequestModelTest(TestCase):

    def test_is_expired_false(self):
        user = make_user()
        req = make_email_change(user, expired=False)
        self.assertFalse(req.is_expired())

    def test_is_expired_true(self):
        user = make_user()
        req = make_email_change(user, expired=True)
        self.assertTrue(req.is_expired())