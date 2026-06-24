from django.test import TestCase
from rest_framework.test import APIClient
from users.tests.factories import make_coordinador, make_docente, make_estudiante, get_auth_header
from users.models import User


class UserFilterTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord@test.com', nombre='Carlos Coord')
        self.docente = make_docente(email='doc@test.com', nombre='Diana Docente')
        self.est1 = make_estudiante(email='est1@test.com', nombre='Elena Estudiante')
        self.est2 = make_estudiante(email='est2@test.com', nombre='Eduardo Est', estado=False)
        self.headers = get_auth_header(self.client, self.coord)

    def test_search_por_nombre(self):
        response = self.client.get(
            '/api/users/?search=Elena',
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        nombres = [u['nombre'] for u in response.data['results']]
        self.assertIn('Elena Estudiante', nombres)
        self.assertNotIn('Diana Docente', nombres)

    def test_search_por_email(self):
        response = self.client.get(
            '/api/users/?search=est1',
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('est1' in u['email'] for u in response.data['results']))

    def test_filtro_por_rol(self):
        response = self.client.get(
            f'/api/users/?rol={User.Rol.ESTUDIANTE}',
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        roles = [u['rol'] for u in response.data['results']]
        self.assertTrue(all(r == User.Rol.ESTUDIANTE for r in roles))

    def test_filtro_por_estado_false(self):
        response = self.client.get(
            '/api/users/?estado=false',
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        estados = [u['estado'] for u in response.data['results']]
        self.assertTrue(all(e is False for e in estados))

    def test_paginacion_retorna_estructura_correcta(self):
        response = self.client.get('/api/users/', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)

    def test_page_size_personalizado(self):
        response = self.client.get(
            '/api/users/?page_size=1',
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)