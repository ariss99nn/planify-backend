# competencia/tests/test_views.py
"""
Tests de las vistas del módulo competencia.

BUG DE URL DETECTADO:
Las URLs del módulo competencia tienen doble prefijo debido a cómo
competencia_urls.py declara los paths y cómo core/urls.py los incluye.

URLs REALES (con doble prefijo):
  Asignaturas   : /api/asignaturas/asignaturas/
                  /api/asignaturas/asignaturas/crear/
                  /api/asignaturas/asignaturas/<pk>/
                  /api/asignaturas/asignaturas/<pk>/editar/
  Competencias  : /api/competencias/competencias/
                  /api/competencias/competencias/crear/
  Resultados    : /api/resultados/resultados/
                  /api/resultados/resultados/crear/

Este es un bug de diseño que debe corregirse en core/urls.py
montando los patterns en 'api/' en lugar de 'api/asignaturas/' etc.
Mientras tanto los tests usan las URLs reales.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from users.tests.factories import (
    make_coordinador, make_docente, make_estudiante, get_auth_header,
)
from competencia.tests.factories import (
    make_asignatura, make_competencia, make_competencia_transversal, make_rap,
)
from programa.tests.factories import make_modulo
from competencia.models.asignatura_model import Asignatura
from competencia.models.competencia_model import Competencia

# URLs con doble prefijo (bug existente)
ASIG = '/api/asignaturas/asignaturas'
COMP = '/api/competencias/competencias'
RAP  = '/api/resultados/resultados'


class AsignaturaViewTest(TestCase):

    def setUp(self):
        self.client     = APIClient()
        self.coord      = make_coordinador(email='coord_a@t.com')
        self.docente    = make_docente(email='doc_a@t.com')
        self.estudiante = make_estudiante(email='est_a@t.com')
        self.asignatura = make_asignatura()

    def test_coordinador_lista_todas(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{ASIG}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('results', r.data)

    def test_estudiante_puede_listar(self):
        """Estudiantes tienen acceso de solo lectura."""
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'{ASIG}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_sin_autenticacion_retorna_401(self):
        self.assertEqual(self.client.get(f'{ASIG}/').status_code, 401)

    def test_coordinador_crea_asignatura(self):
        modulo = make_modulo()
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{ASIG}/crear/', {
            'modulo': modulo.pk,
            'nombre': 'Nueva Asignatura',
            'tipo': Asignatura.Tipo.TEORICA,
            'horas_lectivas': 60,
            'horas_practicas': 0,
            'orden': 99,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear(self):
        modulo = make_modulo()
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post(f'{ASIG}/crear/', {
            'modulo': modulo.pk,
            'nombre': 'Intento',
            'tipo': Asignatura.Tipo.TEORICA,
            'horas_lectivas': 60,
            'horas_practicas': 0,
            'orden': 100,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_horas_lectivas_cero_retorna_400(self):
        modulo = make_modulo()
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{ASIG}/crear/', {
            'modulo': modulo.pk,
            'nombre': 'Sin Horas',
            'tipo': Asignatura.Tipo.TEORICA,
            'horas_lectivas': 0,
            'horas_practicas': 0,
            'orden': 101,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_detalle_asignatura(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{ASIG}/{self.asignatura.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_inexistente_retorna_404(self):
        headers = get_auth_header(self.client, self.coord)
        self.assertEqual(
            self.client.get(f'{ASIG}/99999/', **headers).status_code, 404
        )

    def test_actualiza_asignatura(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{ASIG}/{self.asignatura.pk}/editar/',
            {'nombre': 'Nombre Actualizado'},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)


class CompetenciaViewTest(TestCase):

    def setUp(self):
        self.client     = APIClient()
        self.coord      = make_coordinador(email='coord_c@t.com')
        self.docente    = make_docente(email='doc_c@t.com')
        self.asignatura = make_asignatura()
        self.comp       = make_competencia(asignatura=self.asignatura)

    def test_coordinador_lista_todas(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{COMP}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_sin_autenticacion_retorna_401(self):
        self.assertEqual(self.client.get(f'{COMP}/').status_code, 401)

    def test_coordinador_crea_competencia_principal(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{COMP}/crear/', {
            'asignatura': self.asignatura.pk,
            'codigo': 'NUEVA-COMP-001',
            'nombre': 'Competencia Nueva',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_codigo_duplicado_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{COMP}/crear/', {
            'asignatura': self.asignatura.pk,
            'codigo': self.comp.codigo,
            'nombre': 'Duplicada',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_docente_no_puede_crear(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post(f'{COMP}/crear/', {
            'asignatura': self.asignatura.pk,
            'codigo': 'DOCENTE-001',
            'nombre': 'Intento',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_crea_competencia_transversal(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{COMP}/transversales/crear/', {
            'codigo': 'TRANS-VIEW-001',
            'nombre': 'Inducción General',
            'horas_trimestre_transversal': 4,
            'es_induccion': True,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_detalle_competencia(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{COMP}/{self.comp.pk}/', **headers)
        self.assertEqual(r.status_code, 200)


class RAPViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord  = make_coordinador(email='coord_r@t.com')
        self.docente = make_docente(email='doc_r@t.com')
        self.comp   = make_competencia()
        self.rap    = make_rap(competencia=self.comp)

    def test_coordinador_lista_todos(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{RAP}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_sin_autenticacion_retorna_401(self):
        self.assertEqual(self.client.get(f'{RAP}/').status_code, 401)

    def test_coordinador_crea_rap(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{RAP}/crear/', {
            'competencia': self.comp.pk,
            'codigo': 'RAP-NUEVO-001',
            'descripcion': 'Aplica técnicas de análisis.',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_codigo_duplicado_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{RAP}/crear/', {
            'competencia': self.comp.pk,
            'codigo': self.rap.codigo,
            'descripcion': 'Duplicado.',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_docente_no_puede_crear(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post(f'{RAP}/crear/', {
            'competencia': self.comp.pk,
            'codigo': 'RAP-DOC-001',
            'descripcion': 'Intento.',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_detalle_rap(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{RAP}/{self.rap.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_actualiza_rap(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{RAP}/{self.rap.pk}/editar/',
            {'descripcion': 'Descripción actualizada.'},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)