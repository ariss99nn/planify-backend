from django.test import TestCase
from rest_framework.test import APIClient
from docentes.tests.factories import make_docente, make_docente_user
from users.tests.factories import make_coordinador, get_auth_header


class DocenteFilterTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord@test.com')
        self.headers = get_auth_header(self.client, self.coord)

        u1 = make_docente_user(email='mat@test.com', nombre='Ana Matemáticas')
        u2 = make_docente_user(email='fis@test.com', nombre='Luis Física')
        u3 = make_docente_user(email='qui@test.com', nombre='María Química')

        self.d1 = make_docente(user=u1, especialidad='Matemáticas', estado=True)
        self.d2 = make_docente(user=u2, especialidad='Física', estado=True)
        self.d3 = make_docente(user=u3, especialidad='Química', estado=False)

    def test_search_por_nombre(self):
        response = self.client.get('/api/docentes/?search=Ana', **self.headers)
        self.assertEqual(response.status_code, 200)
        nombres = [d['nombre'] for d in response.data['results']]
        self.assertIn('Ana Matemáticas', nombres)
        self.assertNotIn('Luis Física', nombres)

    def test_search_por_especialidad(self):
        response = self.client.get('/api/docentes/?search=Física', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            any('Física' in d['especialidad'] for d in response.data['results'])
        )

    def test_filtro_especialidad_exacto(self):
        response = self.client.get(
            '/api/docentes/?especialidad=Matemáticas', **self.headers
        )
        self.assertEqual(response.status_code, 200)
        especialidades = [d['especialidad'] for d in response.data['results']]
        self.assertTrue(all('Matemáticas' in e for e in especialidades))

    def test_filtro_estado_false(self):
        response = self.client.get('/api/docentes/?estado=false', **self.headers)
        self.assertEqual(response.status_code, 200)
        estados = [d['estado'] for d in response.data['results']]
        self.assertTrue(all(e is False for e in estados))

    def test_paginacion_estructura(self):
        response = self.client.get('/api/docentes/', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)

    def test_page_size(self):
        response = self.client.get('/api/docentes/?page_size=1', **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)