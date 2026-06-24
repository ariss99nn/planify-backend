from django.test import TestCase
from rest_framework.test import APIClient
from competencia.tests.factories import (
    make_asignatura, make_competencia, make_rap,
)
from competencia.models.asignatura_model import Asignatura
from programa.tests.factories import make_modulo, make_version
from users.tests.factories import make_coordinador, get_auth_header


class AsignaturaFilterTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_af@test.com')
        self.headers = get_auth_header(self.client, self.coord)
        self.modulo = make_modulo()

        self.a1 = make_asignatura(
            modulo=self.modulo, nombre='Programación',
            tipo=Asignatura.Tipo.PRACTICA,
            estado=Asignatura.Estado.ACTIVA,
        )
        self.a2 = make_asignatura(
            modulo=self.modulo, nombre='Bases de Datos',
            tipo=Asignatura.Tipo.TEORICA,
            estado=Asignatura.Estado.INACTIVA,
        )

    def test_search_por_nombre(self):
        r = self.client.get('/api/asignaturas/?search=Programación', **self.headers)
        self.assertEqual(r.status_code, 200)
        nombres = [a['nombre'] for a in r.data['results']]
        self.assertIn('Programación', nombres)
        self.assertNotIn('Bases de Datos', nombres)

    def test_filtro_tipo(self):
        r = self.client.get(
            f'/api/asignaturas/?tipo={Asignatura.Tipo.PRACTICA}', **self.headers
        )
        self.assertEqual(r.status_code, 200)
        tipos = [a['tipo'] for a in r.data['results']]
        self.assertTrue(all(t == Asignatura.Tipo.PRACTICA for t in tipos))

    def test_filtro_estado(self):
        r = self.client.get(
            f'/api/asignaturas/?estado={Asignatura.Estado.INACTIVA}', **self.headers
        )
        self.assertEqual(r.status_code, 200)
        estados = [a['estado'] for a in r.data['results']]
        self.assertTrue(all(e == Asignatura.Estado.INACTIVA for e in estados))

    def test_filtro_modulo(self):
        otro_modulo = make_modulo()
        make_asignatura(modulo=otro_modulo, nombre='Otra')
        r = self.client.get(
            f'/api/asignaturas/?modulo={self.modulo.pk}', **self.headers
        )
        self.assertEqual(r.status_code, 200)
        ids = [a['id'] for a in r.data['results']]
        self.assertIn(self.a1.pk, ids)
        self.assertIn(self.a2.pk, ids)

    def test_paginacion_estructura(self):
        r = self.client.get('/api/asignaturas/', **self.headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('count', r.data)
        self.assertIn('results', r.data)


class CompetenciaFilterTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_cf@test.com')
        self.headers = get_auth_header(self.client, self.coord)
        self.asignatura = make_asignatura()
        self.c1 = make_competencia(asignatura=self.asignatura, nombre='Analizar')
        self.c2 = make_competencia(asignatura=self.asignatura, nombre='Diseñar')

    def test_search_por_nombre(self):
        r = self.client.get('/api/competencias/?search=Analizar', **self.headers)
        self.assertEqual(r.status_code, 200)
        nombres = [c['nombre'] for c in r.data['results']]
        self.assertIn('Analizar', nombres)

    def test_filtro_asignatura(self):
        otra_asignatura = make_asignatura()
        make_competencia(asignatura=otra_asignatura, nombre='Otra')
        r = self.client.get(
            f'/api/competencias/?asignatura={self.asignatura.pk}', **self.headers
        )
        self.assertEqual(r.status_code, 200)
        ids = [c['id'] for c in r.data['results']]
        self.assertIn(self.c1.pk, ids)
        self.assertIn(self.c2.pk, ids)

    def test_paginacion_competencia(self):
        r = self.client.get('/api/competencias/', **self.headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('count', r.data)
        self.assertIn('results', r.data)