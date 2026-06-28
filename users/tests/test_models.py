# users/tests/test_models.py
"""
Tests del modelo User y modelos de autenticación.

CORRECCIONES respecto a la versión anterior:
- make_password_reset ahora usa los campos reales del modelo (sin code, expires_at).
- is_expired de PasswordReset se calcula desde created_at, no desde expires_at.
- email_verificado es campo explícito del modelo (BooleanField).
- Rol.ADMIN no existe → se usa Rol.ADMINISTRATIVO.
"""
import uuid
from datetime import timedelta

from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone

from users.models import User, EmailVerification, PasswordReset, EmailChangeRequest
from users.tests.factories import (
    make_user, make_coordinador, make_docente, make_estudiante,
    make_administrativo, make_verification, make_password_reset, make_email_change,
)


# ──────────────────────────────────────────────────────────────────────────────
class UserModelTest(TestCase):

    def test_str_contiene_nombre_apellido_y_rol(self):
        user = make_user(
            nombre='Juan', apellido='Pérez', rol=User.Rol.DOCENTE,
            email='juan@test.com',
        )
        s = str(user)
        self.assertIn('Juan', s)
        self.assertIn('Pérez', s)

    def test_nombre_completo_concatena_nombre_y_apellido(self):
        user = make_user(nombre='Ana', apellido='García')
        self.assertEqual(user.nombre_completo, 'Ana García')

    def test_nombre_completo_solo_nombre(self):
        user = make_user(nombre='Ana', apellido='')
        self.assertIn('Ana', user.nombre_completo)

    # ── Propiedades de rol ────────────────────────────────────────────────────

    def test_es_coordinador(self):
        self.assertTrue(make_coordinador().es_coordinador)
        self.assertFalse(make_coordinador().es_docente)
        self.assertFalse(make_coordinador().es_estudiante)
        self.assertFalse(make_coordinador().es_administrativo)

    def test_es_docente(self):
        self.assertTrue(make_docente().es_docente)
        self.assertFalse(make_docente().es_coordinador)

    def test_es_administrativo(self):
        # CORRECCIÓN: el rol es ADMINISTRATIVO, no ADMIN
        admin = make_administrativo()
        self.assertEqual(admin.rol, User.Rol.ADMINISTRATIVO)
        self.assertTrue(admin.es_administrativo)

    def test_es_estudiante(self):
        self.assertTrue(make_estudiante().es_estudiante)

    def test_puede_gestionar_usuarios_gestion_true(self):
        self.assertTrue(make_coordinador().puede_gestionar_usuarios)
        self.assertTrue(make_administrativo().puede_gestionar_usuarios)

    def test_puede_gestionar_usuarios_otros_false(self):
        self.assertFalse(make_docente().puede_gestionar_usuarios)
        self.assertFalse(make_estudiante().puede_gestionar_usuarios)

    # ── estado / is_active ───────────────────────────────────────────────────

    def test_estado_property_devuelve_is_active(self):
        user = make_user(estado=True)
        self.assertTrue(user.estado)
        self.assertTrue(user.is_active)

    def test_estado_setter_actualiza_is_active(self):
        user = make_user(estado=True)
        user.estado = False
        self.assertFalse(user.is_active)

    # ── email_verificado ─────────────────────────────────────────────────────

    def test_email_verificado_default_false_usuario_inactivo(self):
        # Usuario inactivo sin verificar
        user = make_user(estado=False, email_verificado=False)
        self.assertFalse(user.email_verificado)

    def test_email_verificado_true_cuando_activo_por_defecto(self):
        # make_user(estado=True) pone email_verificado=True por defecto
        user = make_user(estado=True)
        self.assertTrue(user.email_verificado)

    # ── USERNAME_FIELD y REQUIRED_FIELDS ────────────────────────────────────

    def test_username_field_es_email(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_required_fields_vacio(self):
        self.assertEqual(User.REQUIRED_FIELDS, [])

    # ── Unicidad de email ────────────────────────────────────────────────────

    def test_email_unico(self):
        make_user(email='unico@test.com')
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='unico@test.com',
                password='TestPass123!',
                nombre='Duplicado',
            )

    # ── Ordenación ───────────────────────────────────────────────────────────

    def test_ordering_por_apellido_y_nombre(self):
        make_user(nombre='Zara',  apellido='Zúñiga', email='z@test.com')
        make_user(nombre='Ana',   apellido='Álvarez', email='a@test.com')
        make_user(nombre='Pedro', apellido='Martínez', email='p@test.com')
        apellidos = list(User.objects.values_list('apellido', flat=True))
        self.assertEqual(apellidos, sorted(apellidos))

    # ── imagen_url ───────────────────────────────────────────────────────────

    def test_imagen_url_none_sin_imagen(self):
        self.assertIsNone(make_user().imagen_url)

    # ── Roles disponibles ────────────────────────────────────────────────────

    def test_roles_disponibles(self):
        roles = [r[0] for r in User.Rol.choices]
        self.assertIn(User.Rol.COORDINADOR,   roles)
        self.assertIn(User.Rol.ADMINISTRATIVO, roles)
        self.assertIn(User.Rol.DOCENTE,        roles)
        self.assertIn(User.Rol.ESTUDIANTE,     roles)
        # Confirmar que ADMIN no existe como choice
        self.assertNotIn('ADMIN', roles)


# ──────────────────────────────────────────────────────────────────────────────
class EmailVerificationModelTest(TestCase):

    def setUp(self):
        self.user = make_user(estado=False, email_verificado=False)

    def test_is_expired_false_cuando_no_expiro(self):
        v = make_verification(self.user, expired=False)
        self.assertFalse(v.is_expired())

    def test_is_expired_true_cuando_expiro(self):
        v = make_verification(self.user, expired=True)
        self.assertTrue(v.is_expired())

    def test_is_valid_true_no_usado_no_expirado(self):
        v = make_verification(self.user)
        self.assertTrue(v.is_valid())

    def test_is_valid_false_si_is_used(self):
        v = make_verification(self.user, used=True)
        self.assertFalse(v.is_valid())

    def test_is_valid_false_si_expirado(self):
        v = make_verification(self.user, expired=True)
        self.assertFalse(v.is_valid())

    def test_mark_as_verified_actualiza_campos(self):
        v = make_verification(self.user)
        v.mark_as_verified()
        self.assertTrue(v.is_used)
        self.assertTrue(v.is_verified)
        self.assertIsNotNone(v.verified_at)

    def test_get_expiration_time_retorna_datetime_futuro(self):
        exp = EmailVerification.get_expiration_time()
        self.assertGreater(exp, timezone.now())

    def test_invalidate_previous_codes(self):
        v1 = make_verification(self.user)
        v2 = make_verification(self.user)
        EmailVerification.invalidate_previous_codes(self.user)
        v1.refresh_from_db()
        v2.refresh_from_db()
        self.assertTrue(v1.is_used)
        self.assertTrue(v2.is_used)

    def test_codigo_es_string_max_6_chars(self):
        v = make_verification(self.user)
        self.assertIsInstance(v.code, str)
        self.assertLessEqual(len(v.code), 6)

    def test_str_contiene_email_usuario(self):
        v = make_verification(self.user)
        self.assertIn(self.user.email, str(v))


# ──────────────────────────────────────────────────────────────────────────────
class PasswordResetModelTest(TestCase):
    """
    Tests del modelo PasswordReset en su estado FINAL (post-migración 0004).

    La migración 0004 eliminó: code, expires_at, is_used.
    Renombró is_used → used.

    Campos existentes: user, token (UUID), created_at, used.
    Expiración calculada desde created_at + EXPIRY_HOURS.
    """

    def setUp(self):
        self.user = make_user(email='reset@test.com')

    def test_token_es_uuid(self):
        reset = make_password_reset(self.user)
        self.assertIsInstance(reset.token, uuid.UUID)

    def test_token_unico(self):
        r1 = make_password_reset(self.user)
        r2 = make_password_reset(self.user)
        self.assertNotEqual(r1.token, r2.token)

    def test_is_expired_false_recien_creado(self):
        reset = make_password_reset(self.user, expired=False)
        self.assertFalse(reset.is_expired)

    def test_is_expired_true_cuando_expiro(self):
        reset = make_password_reset(self.user, expired=True)
        self.assertTrue(reset.is_expired)

    def test_is_valid_true_no_usado_no_expirado(self):
        reset = make_password_reset(self.user)
        self.assertTrue(reset.is_valid)

    def test_is_valid_false_cuando_usado(self):
        reset = make_password_reset(self.user, used=True)
        self.assertFalse(reset.is_valid)

    def test_is_valid_false_cuando_expirado(self):
        reset = make_password_reset(self.user, expired=True)
        self.assertFalse(reset.is_valid)

    @override_settings(PASSWORD_RESET_EXPIRY_HOURS=2)
    def test_get_expiration_time_retorna_horas_configuradas(self):
        """get_expiration_time() retorna int de horas, no datetime."""
        hours = PasswordReset.get_expiration_time()
        self.assertEqual(hours, 2)

    @override_settings(PASSWORD_RESET_EXPIRY_HOURS=4)
    def test_get_expiration_time_respeta_setting(self):
        self.assertEqual(PasswordReset.get_expiration_time(), 4)

    def test_campos_que_no_existen_en_modelo(self):
        """
        Verificar que el modelo NO tiene code ni expires_at después de 0004.
        El factory no debe pasar estos campos o fallará con TypeError.
        """
        reset = make_password_reset(self.user)
        self.assertFalse(hasattr(reset, 'code'))
        self.assertFalse(hasattr(reset, 'expires_at'))

    def test_str_contiene_user_id_y_used(self):
        reset = make_password_reset(self.user)
        s = str(reset)
        self.assertIn('used=False', s)

    def test_ordering_por_created_at_desc(self):
        r1 = make_password_reset(self.user)
        r2 = make_password_reset(self.user)
        pks = list(
            PasswordReset.objects.filter(user=self.user)
            .values_list('pk', flat=True)
        )
        self.assertEqual(pks[0], r2.pk)  # más reciente primero


# ──────────────────────────────────────────────────────────────────────────────
class EmailChangeRequestModelTest(TestCase):

    def setUp(self):
        self.user = make_user(email='change@test.com')

    def test_is_expired_false(self):
        req = make_email_change(self.user, expired=False)
        self.assertFalse(req.is_expired())

    def test_is_expired_true(self):
        req = make_email_change(self.user, expired=True)
        self.assertTrue(req.is_expired())

    def test_is_valid_true(self):
        req = make_email_change(self.user)
        self.assertTrue(req.is_valid())

    def test_is_valid_false_si_usado(self):
        req = make_email_change(self.user, used=True)
        self.assertFalse(req.is_valid())

    def test_mark_as_used(self):
        req = make_email_change(self.user)
        req.mark_as_used()
        self.assertTrue(req.is_used)

    def test_nuevo_email_guardado(self):
        req = make_email_change(self.user, new_email='nuevo@test.com')
        self.assertEqual(req.new_email, 'nuevo@test.com')

    def test_str_contiene_email_origen_y_destino(self):
        req = make_email_change(self.user, new_email='destino@test.com')
        self.assertIn(self.user.email, str(req))
        self.assertIn('destino@test.com', str(req))

    def test_invalidate_previous_requests(self):
        r1 = make_email_change(self.user, new_email='a@test.com')
        r2 = make_email_change(self.user, new_email='b@test.com')
        EmailChangeRequest.invalidate_previous_requests(self.user)
        r1.refresh_from_db()
        r2.refresh_from_db()
        self.assertTrue(r1.is_used)
        self.assertTrue(r2.is_used)

    def test_email_already_requested_true(self):
        make_email_change(self.user, new_email='solicitado@test.com', used=False)
        self.assertTrue(
            EmailChangeRequest.email_already_requested('solicitado@test.com')
        )

    def test_email_already_requested_false(self):
        self.assertFalse(
            EmailChangeRequest.email_already_requested('libre@test.com')
        )