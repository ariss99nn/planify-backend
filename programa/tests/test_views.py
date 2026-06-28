# programa/tests/test_views.py
"""
Tests de las vistas del módulo programa.

CORRECCIONES:
- URL base /api/ (sin /v1/).
- make_programa, make_version, make_modulo ya existen en factories.py.
- Estudiante accede a /api/programas/ pero ve solo su programa.
"""
from datetime import date
from django.test import TestCase
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError

from users.tests.factories import (
    make_coordinador, make_docente, make_estudiante, get_auth_header,
)
from programa.tests.factories import make_programa, make_version, make_modulo
from programa.models.programa_model import Programa
from programa.models.version_programa_model import VersionPrograma
from programa.models.modulo_model import Modulo

P  = '/api/programas'
V  = '/api/versiones'
M  = '/api/modulos'


class ProgramaListViewTest(TestCase):

    def setUp(self):
        self.client     = APIClient()
        self.coord      = make_coordinador(email='coord_p@t.com')
        self.docente    = make_docente(email='doc_p@t.com')
        self.estudiante = make_estudiante(email='est_p@t.com')
        self.programa   = make_programa(nombre='Programa Test')
        self.version    = make_version(programa=self.programa, vigente=True)

    def test_coordinador_lista_todos(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{P}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('results', r.data)

    def test_docente_lista_todos(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'{P}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_sin_autenticacion_retorna_401(self):
        self.assertEqual(self.client.get(f'{P}/').status_code, 401)

    def test_paginacion_presente(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{P}/', **headers)
        self.assertIn('count',   r.data)
        self.assertIn('results', r.data)

    def test_estudiante_sin_ficha_activa_lista_vacio(self):
        """Estudiante sin ficha activa → lista vacía (su programa no está en fichas activas)."""
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'{P}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.get('count', 0), 0)


class ProgramaCreateViewTest(TestCase):

    def setUp(self):
        self.client  = APIClient()
        self.coord   = make_coordinador(email='coord_pc@t.com')
        self.docente = make_docente(email='doc_pc@t.com')

    def test_coordinador_crea_programa_retorna_201(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{P}/create/', {
            'nombre': 'Nuevo Programa',
            'nivel': Programa.Nivel.TECNOLOGIA,
            'horas_lectivas': 1200,
            'horas_practicas': 600,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_horas_lectivas_cero_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{P}/create/', {
            'nombre': 'Sin Horas',
            'nivel': Programa.Nivel.TECNICO,
            'horas_lectivas': 0,
            'horas_practicas': 0,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_docente_no_puede_crear(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post(f'{P}/create/', {
            'nombre': 'Intento',
            'nivel': Programa.Nivel.TECNICO,
            'horas_lectivas': 100,
            'horas_practicas': 50,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_autenticacion_retorna_401(self):
        r = self.client.post(f'{P}/create/', {
            'nombre': 'Sin Auth',
            'nivel': Programa.Nivel.TECNICO,
            'horas_lectivas': 100,
            'horas_practicas': 50,
        }, format='json')
        self.assertEqual(r.status_code, 401)

    def test_cadena_formacion_sin_trimestres_cadena_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{P}/create/', {
            'nombre': 'Cadena Sin Trimestres',
            'nivel': Programa.Nivel.TECNICO,
            'horas_lectivas': 800,
            'horas_practicas': 400,
            'tipo_formacion': Programa.TipoFormacion.CADENA_FORMACION,
            'trimestres_totales': 6,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)


class ProgramaDetailViewTest(TestCase):

    def setUp(self):
        self.client   = APIClient()
        self.coord    = make_coordinador(email='coord_pd@t.com')
        self.docente  = make_docente(email='doc_pd@t.com')
        self.programa = make_programa()

    def test_coordinador_ve_detalle(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{P}/{self.programa.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_ve_detalle(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'{P}/{self.programa.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_inexistente_retorna_404(self):
        headers = get_auth_header(self.client, self.coord)
        self.assertEqual(
            self.client.get(f'{P}/99999/', **headers).status_code, 404
        )

    def test_estudiante_sin_ficha_activa_retorna_403(self):
        est = make_estudiante(email='est_pd@t.com')
        headers = get_auth_header(self.client, est)
        r = self.client.get(f'{P}/{self.programa.pk}/', **headers)
        self.assertEqual(r.status_code, 403)


class ProgramaUpdateViewTest(TestCase):

    def setUp(self):
        self.client   = APIClient()
        self.coord    = make_coordinador(email='coord_pu@t.com')
        self.docente  = make_docente(email='doc_pu@t.com')
        self.programa = make_programa()

    def test_coordinador_actualiza_nombre(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{P}/{self.programa.pk}/update/',
            {'nombre': 'Nombre Actualizado'},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.programa.refresh_from_db()
        self.assertEqual(self.programa.nombre, 'Nombre Actualizado')

    def test_docente_no_puede_actualizar(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.patch(
            f'{P}/{self.programa.pk}/update/',
            {'nombre': 'Intento'},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 403)


class VersionViewTest(TestCase):

    def setUp(self):
        self.client   = APIClient()
        self.coord    = make_coordinador(email='coord_v@t.com')
        self.docente  = make_docente(email='doc_v@t.com')
        self.programa = make_programa()
        self.version  = make_version(programa=self.programa, numero=1)

    def test_lista_versiones(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{V}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_crea_version(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{V}/create/', {
            'programa': self.programa.pk,
            'numero': 10,
            'vigente': False,
            'fecha_inicio': '2024-01-01',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_numero_duplicado_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{V}/create/', {
            'programa': self.programa.pk,
            'numero': 1,  # ya existe
            'vigente': False,
            'fecha_inicio': '2024-06-01',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_docente_no_puede_crear_version(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post(f'{V}/create/', {
            'programa': self.programa.pk,
            'numero': 20,
            'vigente': False,
            'fecha_inicio': '2024-01-01',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_detalle_version(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{V}/{self.version.pk}/', **headers)
        self.assertEqual(r.status_code, 200)


class ModuloViewTest(TestCase):

    def setUp(self):
        self.client  = APIClient()
        self.coord   = make_coordinador(email='coord_m@t.com')
        self.docente = make_docente(email='doc_m@t.com')
        self.version = make_version()
        self.modulo  = make_modulo(version=self.version, orden=1)

    def test_lista_modulos(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{M}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_crea_modulo(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{M}/create/', {
            'version': self.version.pk,
            'nombre': 'Nuevo Modulo',
            'orden': 99,
            'horas_lectivas': 60,
            'horas_practicas': 30,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_orden_duplicado_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{M}/create/', {
            'version': self.version.pk,
            'nombre': 'Duplicado',
            'orden': 1,  # ya existe
            'horas_lectivas': 60,
            'horas_practicas': 30,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_docente_no_puede_crear_modulo(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post(f'{M}/create/', {
            'version': self.version.pk,
            'nombre': 'Intento',
            'orden': 50,
            'horas_lectivas': 40,
            'horas_practicas': 20,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_actualiza_modulo(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{M}/{self.modulo.pk}/update/',
            {'nombre': 'Módulo Actualizado'},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)