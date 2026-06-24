from datetime import date
from django.test import TestCase
from rest_framework.test import APIClient
from programa.tests.factories import make_programa, make_version, make_modulo
from programa.models.programa_model import Programa
from programa.models.modulo_model import Modulo
from users.tests.factories import make_coordinador, get_auth_header


class ProgramaFilterTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_pf@test.com')
        self.headers = get_auth_header(self.client, self.coord)

        self.p1 = make_programa(
            nombre='Sistemas', nivel=Programa.Nivel.TECNICO,
            estado=Programa.Estado.ACTIVO,
        )
        self.p2 = make_programa(
            nombre='Contabilidad', nivel=Programa.Nivel.TECNOLOGIA,
            estado=Programa.Estado.INACTIVO,
        )
        self.p3 = make_programa(
            nombre='Marketing Digital', nivel=Programa.Nivel.CURSO_CORTO,
            estado=Programa.Estado.ACTIVO,
        )

    def test_search_por_nombre(self):
        r = self.client.get('/api/programas/?search=Sistemas', **self.headers)
        self.assertEqual(r.status_code, 200)
        nombres = [p['nombre'] for p in r.data['results']]
        self.assertIn('Sistemas', nombres)
        self.assertNotIn('Contabilidad', nombres)

    def test_filtro_nivel(self):
        r = self.client.get(
            f'/api/programas/?nivel={Programa.Nivel.TECNOLOGIA}',
            **self.headers,
        )
        self.assertEqual(r.status_code, 200)
        niveles = [p['nivel'] for p in r.data['results']]
        self.assertTrue(all(n == Programa.Nivel.TECNOLOGIA for n in niveles))

    def test_filtro_estado(self):
        r = self.client.get(
            f'/api/programas/?estado={Programa.Estado.INACTIVO}',
            **self.headers,
        )
        self.assertEqual(r.status_code, 200)
        estados = [p['estado'] for p in r.data['results']]
        self.assertTrue(all(e == Programa.Estado.INACTIVO for e in estados))

    def test_paginacion_estructura(self):
        r = self.client.get('/api/programas/', **self.headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('count', r.data)
        self.assertIn('results', r.data)

    def test_page_size(self):
        r = self.client.get('/api/programas/?page_size=1', **self.headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)


class ModuloFilterTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_mf@test.com')
        self.headers = get_auth_header(self.client, self.coord)

        self.version = make_version()
        self.m1 = make_modulo(
            version=self.version, nombre='Programación',
            estado=Modulo.Estado.ACTIVO,
        )
        self.m2 = make_modulo(
            version=self.version, nombre='Bases de Datos',
            estado=Modulo.Estado.INACTIVO,
        )

    def test_filtro_version(self):
        r = self.client.get(
            f'/api/modulos/?version={self.version.pk}',
            **self.headers,
        )
        self.assertEqual(r.status_code, 200)
        ids = [m['id'] for m in r.data['results']]
        self.assertIn(self.m1.pk, ids)
        self.assertIn(self.m2.pk, ids)

    def test_filtro_estado_modulo(self):
        r = self.client.get(
            f'/api/modulos/?estado={Modulo.Estado.INACTIVO}',
            **self.headers,
        )
        self.assertEqual(r.status_code, 200)
        estados = [m['estado'] for m in r.data['results']]
        self.assertTrue(all(e == Modulo.Estado.INACTIVO for e in estados))

    def test_search_modulo(self):
        r = self.client.get('/api/modulos/?search=Programación', **self.headers)
        self.assertEqual(r.status_code, 200)
        nombres = [m['nombre'] for m in r.data['results']]
        self.assertIn('Programación', nombres)