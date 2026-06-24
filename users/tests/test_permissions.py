from django.test import TestCase, RequestFactory
from users.tests.factories import (
    make_coordinador, make_administrativo, make_docente, make_estudiante
)
from users.permissions import (
    IsManager, IsCoordinador, IsDocente, IsEstudiante,
    IsAdministrativo, IsStaffLike, CanManageUser,
)
from users.models import User


class RolePermissionsTest(TestCase):

    def _make_request(self, user):
        request = RequestFactory().get('/')
        request.user = user
        return request

    def test_is_manager_coord_y_admin(self):
        perm = IsManager()
        self.assertTrue(perm.has_permission(self._make_request(make_coordinador(email='c1@test.com')), None))
        self.assertTrue(perm.has_permission(self._make_request(make_administrativo(email='a1@test.com')), None))
        self.assertFalse(perm.has_permission(self._make_request(make_docente(email='d1@test.com')), None))
        self.assertFalse(perm.has_permission(self._make_request(make_estudiante(email='e1@test.com')), None))

    def test_is_coordinador(self):
        perm = IsCoordinador()
        self.assertTrue(perm.has_permission(self._make_request(make_coordinador(email='c2@test.com')), None))
        self.assertFalse(perm.has_permission(self._make_request(make_administrativo(email='a2@test.com')), None))

    def test_is_docente(self):
        perm = IsDocente()
        self.assertTrue(perm.has_permission(self._make_request(make_docente(email='d2@test.com')), None))
        self.assertFalse(perm.has_permission(self._make_request(make_estudiante(email='e2@test.com')), None))

    def test_is_staff_like(self):
        perm = IsStaffLike()
        self.assertTrue(perm.has_permission(self._make_request(make_docente(email='d3@test.com')), None))
        self.assertTrue(perm.has_permission(self._make_request(make_coordinador(email='c3@test.com')), None))
        self.assertFalse(perm.has_permission(self._make_request(make_estudiante(email='e3@test.com')), None))


class CanManageUserTest(TestCase):

    def _make_request(self, user):
        request = RequestFactory().patch('/')
        request.user = user
        return request

    def test_coord_puede_gestionar_estudiante(self):
        coord = make_coordinador(email='coord@test.com')
        estudiante = make_estudiante(email='est@test.com')
        perm = CanManageUser()
        request = self._make_request(coord)
        self.assertTrue(perm.has_object_permission(request, None, estudiante))

    def test_nadie_puede_gestionarse_a_si_mismo(self):
        coord = make_coordinador(email='coord2@test.com')
        perm = CanManageUser()
        request = self._make_request(coord)
        self.assertFalse(perm.has_object_permission(request, None, coord))

    def test_docente_no_puede_gestionar(self):
        docente = make_docente(email='doc@test.com')
        estudiante = make_estudiante(email='est2@test.com')
        perm = CanManageUser()
        request = self._make_request(docente)
        self.assertFalse(perm.has_permission(request, None))

    def test_admin_puede_gestionar_cualquiera(self):
        admin = make_administrativo(email='admin@test.com')
        docente = make_docente(email='doc2@test.com')
        perm = CanManageUser()
        request = self._make_request(admin)
        self.assertTrue(perm.has_object_permission(request, None, docente))

    def test_estudiante_no_puede_gestionar(self):
        est = make_estudiante(email='est3@test.com')
        otro = make_estudiante(email='est4@test.com')
        perm = CanManageUser()
        request = self._make_request(est)
        self.assertFalse(perm.has_permission(request, None))