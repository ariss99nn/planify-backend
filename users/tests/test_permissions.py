# users/tests/test_permissions.py
"""Tests de las clases de permiso."""
from django.test import TestCase, RequestFactory
from users.tests.factories import (
    make_coordinador, make_docente, make_estudiante,
    make_user, make_administrativo,
)
from users.models import User


class PermissionsTest(TestCase):

    def _req(self, user, method='GET'):
        req = getattr(RequestFactory(), method.lower())('/')
        req.user = user
        return req

    # ── IsManager ────────────────────────────────────────────────────────────

    def test_is_manager_coord(self):
        from users.permissions import IsManager
        perm = IsManager()
        self.assertTrue(perm.has_permission(
            self._req(make_coordinador(email='c1@t.com')), None
        ))

    def test_is_manager_administrativo(self):
        from users.permissions import IsManager
        perm = IsManager()
        self.assertTrue(perm.has_permission(
            self._req(make_administrativo(email='a1@t.com')), None
        ))

    def test_is_manager_docente_false(self):
        from users.permissions import IsManager
        perm = IsManager()
        self.assertFalse(perm.has_permission(
            self._req(make_docente(email='d1@t.com')), None
        ))

    def test_is_manager_estudiante_false(self):
        from users.permissions import IsManager
        perm = IsManager()
        self.assertFalse(perm.has_permission(
            self._req(make_estudiante(email='e1@t.com')), None
        ))

    # ── IsCoordinador ─────────────────────────────────────────────────────────

    def test_is_coordinador_true(self):
        from users.permissions import IsCoordinador
        perm = IsCoordinador()
        self.assertTrue(perm.has_permission(
            self._req(make_coordinador(email='c2@t.com')), None
        ))

    def test_is_coordinador_administrativo_false(self):
        from users.permissions import IsCoordinador
        perm = IsCoordinador()
        self.assertFalse(perm.has_permission(
            self._req(make_administrativo(email='a2@t.com')), None
        ))

    # ── IsDocente ─────────────────────────────────────────────────────────────

    def test_is_docente_true(self):
        from users.permissions import IsDocente
        perm = IsDocente()
        self.assertTrue(perm.has_permission(
            self._req(make_docente(email='d2@t.com')), None
        ))

    def test_is_docente_estudiante_false(self):
        from users.permissions import IsDocente
        perm = IsDocente()
        self.assertFalse(perm.has_permission(
            self._req(make_estudiante(email='e2@t.com')), None
        ))

    # ── IsAdministrativo ──────────────────────────────────────────────────────

    def test_is_administrativo_true(self):
        from users.permissions import IsAdministrativo
        perm = IsAdministrativo()
        self.assertTrue(perm.has_permission(
            self._req(make_administrativo(email='a3@t.com')), None
        ))

    def test_is_administrativo_coord_false(self):
        from users.permissions import IsAdministrativo
        perm = IsAdministrativo()
        self.assertFalse(perm.has_permission(
            self._req(make_coordinador(email='c3@t.com')), None
        ))

    # ── IsStaffLike ───────────────────────────────────────────────────────────

    def test_is_staff_like_docente(self):
        from users.permissions import IsStaffLike
        perm = IsStaffLike()
        self.assertTrue(perm.has_permission(
            self._req(make_docente(email='d3@t.com')), None
        ))

    def test_is_staff_like_coord(self):
        from users.permissions import IsStaffLike
        perm = IsStaffLike()
        self.assertTrue(perm.has_permission(
            self._req(make_coordinador(email='c4@t.com')), None
        ))

    def test_is_staff_like_estudiante_false(self):
        from users.permissions import IsStaffLike
        perm = IsStaffLike()
        self.assertFalse(perm.has_permission(
            self._req(make_estudiante(email='e3@t.com')), None
        ))

    # ── CanManageUser ─────────────────────────────────────────────────────────

    def test_can_manage_user_coord_puede_gestionar_estudiante(self):
        from users.permissions import CanManageUser
        perm = CanManageUser()
        coord = make_coordinador(email='c5@t.com')
        est   = make_estudiante(email='e4@t.com')
        self.assertTrue(perm.has_permission(self._req(coord), None))
        self.assertTrue(perm.has_object_permission(self._req(coord), None, est))

    def test_can_manage_user_nadie_gestiona_a_si_mismo(self):
        from users.permissions import CanManageUser
        perm  = CanManageUser()
        coord = make_coordinador(email='c6@t.com')
        self.assertFalse(perm.has_object_permission(self._req(coord), None, coord))

    def test_can_manage_user_docente_no_tiene_permiso(self):
        from users.permissions import CanManageUser
        perm    = CanManageUser()
        docente = make_docente(email='d4@t.com')
        est     = make_estudiante(email='e5@t.com')
        self.assertFalse(perm.has_permission(self._req(docente), None))

    # ── CanDeactivateOrRestoreCoordinator ─────────────────────────────────────

    def test_can_deactivate_coordinator_solo_coord_puede_desactivar_coord(self):
        from users.permissions import CanDeactivateOrRestoreCoordinator
        perm  = CanDeactivateOrRestoreCoordinator()
        coord1 = make_coordinador(email='c7@t.com')
        coord2 = make_coordinador(email='c8@t.com')
        admin  = make_administrativo(email='a4@t.com')

        # Coord puede operar sobre otro coord
        self.assertTrue(perm.has_object_permission(self._req(coord1), None, coord2))
        # Admin NO puede operar sobre coord
        self.assertFalse(perm.has_object_permission(self._req(admin), None, coord2))
        # Coord puede operar sobre docente (no es coordinador)
        docente = make_docente(email='d5@t.com')
        self.assertTrue(perm.has_object_permission(self._req(admin), None, docente))


# ─────────────────────────────────────────────────────────────────────────────
# users/tests/test_image_cleanup.py
# ─────────────────────────────────────────────────────────────────────────────

from unittest.mock import patch, MagicMock

class UserImageCleanupTest(TestCase):

    def test_borrar_archivo_existente_llama_delete(self):
        from core.signals.image_cleanup import _borrar_archivo
        mock_field = MagicMock()
        mock_field.name = 'usuarios/foto_vieja.jpg'
        mock_field.storage.exists.return_value = True
        _borrar_archivo(mock_field)
        mock_field.storage.delete.assert_called_once_with('usuarios/foto_vieja.jpg')

    def test_borrar_campo_none_no_explota(self):
        from core.signals.image_cleanup import _borrar_archivo
        try:
            _borrar_archivo(None)
        except Exception as e:
            self.fail(f'_borrar_archivo(None) lanzó: {e}')

    def test_borrar_archivo_inexistente_no_llama_delete(self):
        from core.signals.image_cleanup import _borrar_archivo
        mock_field = MagicMock()
        mock_field.name = 'no_existe.jpg'
        mock_field.storage.exists.return_value = False
        _borrar_archivo(mock_field)
        mock_field.storage.delete.assert_not_called()

    def test_pre_save_no_borra_si_imagen_no_cambia(self):
        from core.signals.image_cleanup import _make_pre_save_handler
        from users.models.user import User
        handler = _make_pre_save_handler('imagen')
        user = make_user(email='img1@test.com')
        mock_field = MagicMock()
        mock_field.name = 'mismo.jpg'
        with patch.object(User.objects, 'get') as mock_get:
            old_instance = MagicMock()
            setattr(old_instance, 'imagen', mock_field)
            mock_get.return_value = old_instance
            with patch.object(user, 'imagen', mock_field):
                with patch('core.signals.image_cleanup._borrar_archivo') as mock_borrar:
                    handler(User, user)
                    mock_borrar.assert_not_called()

    def test_pre_save_borra_imagen_anterior_al_cambiar(self):
        from core.signals.image_cleanup import _make_pre_save_handler
        from users.models.user import User
        handler = _make_pre_save_handler('imagen')
        user = make_user(email='img2@test.com')

        old_file = MagicMock()
        old_file.name = 'vieja.jpg'
        old_file.storage.exists.return_value = True

        new_file = MagicMock()
        new_file.name = 'nueva.jpg'

        with patch.object(User.objects, 'get') as mock_get:
            old_instance = MagicMock()
            setattr(old_instance, 'imagen', old_file)
            mock_get.return_value = old_instance
            with patch.object(user, 'imagen', new_file):
                handler(User, user)

        old_file.storage.delete.assert_called_once_with('vieja.jpg')

    def test_post_delete_borra_imagen(self):
        from core.signals.image_cleanup import _make_post_delete_handler
        from users.models.user import User
        handler = _make_post_delete_handler('imagen')
        user = make_user(email='img3@test.com')
        mock_field = MagicMock()
        mock_field.name = 'borrar.jpg'
        mock_field.storage.exists.return_value = True
        with patch.object(user, 'imagen', mock_field):
            handler(User, user)
        mock_field.storage.delete.assert_called_once_with('borrar.jpg')