from datetime import date
from django.test import TestCase
from rest_framework.test import APIClient
from programa.tests.factories import (
    make_programa, make_version, make_modulo,
    make_docente_modulo, make_ficha_para_estudiante,
)
from programa.models.programa_model import Programa
from programa.models.modulo_model import Modulo
from users.tests.factories import (
    make_coordinador, make_administrativo,
    make_docente, make_estudiante, get_auth_header,
)


class ProgramaListViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_pl@test.com')
        self.admin = make_administrativo(email='admin_pl@test.com')
        self.docente = make_docente(email='doc_pl@test.com')
        self.estudiante = make_estudiante(email='est_pl@test.com')
        self.programa = make_programa()
        self.version = make_version(programa=self.programa, vigente=True)

    def test_coord_ve_todos(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/programas/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('results', r.data)

    def test_admin_ve_todos(self):
        headers = get_auth_header(self.client, self.admin)
        r = self.client.get('/api/programas/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_ve_todos(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/programas/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_estudiante_ve_solo_su_programa(self):
        make_ficha_para_estudiante(self.version, self.estudiante)
        otro_programa = make_programa(nombre='Otro Programa')
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get('/api/programas/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [p['id'] for p in r.data['results']]
        self.assertIn(self.programa.pk, ids)
        self.assertNotIn(otro_programa.pk, ids)

    def test_sin_autenticacion(self):
        r = self.client.get('/api/programas/')
        self.assertEqual(r.status_code, 401)


class ProgramaDetailViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_pd@test.com')
        self.estudiante = make_estudiante(email='est_pd@test.com')
        self.programa = make_programa()
        self.version = make_version(programa=self.programa)

    def test_coord_ve_detalle(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'/api/programas/{self.programa.pk}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('versiones', r.data)

    def test_estudiante_con_ficha_ve_detalle(self):
        make_ficha_para_estudiante(self.version, self.estudiante)
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'/api/programas/{self.programa.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_estudiante_sin_ficha_no_ve_detalle(self):
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'/api/programas/{self.programa.pk}/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_no_encontrado(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/programas/99999/', **headers)
        self.assertEqual(r.status_code, 404)


class ProgramaCreateUpdateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_pc@test.com')
        self.docente = make_docente(email='doc_pc@test.com')
        self.programa = make_programa()

    def test_coord_crea_programa(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/programas/create/', {
            'nombre': 'Nuevo Programa',
            'nivel': Programa.Nivel.TECNICO,
            'horas_lectivas': 1200,
            'horas_practicas': 600,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)
        self.assertIn('versiones', r.data)

    def test_docente_no_puede_crear(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/programas/create/', {
            'nombre': 'Intento',
            'nivel': Programa.Nivel.TECNICO,
            'horas_lectivas': 100,
            'horas_practicas': 50,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_coord_actualiza_programa(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/programas/{self.programa.pk}/update/',
            {'nombre': 'Nombre Actualizado'},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.programa.refresh_from_db()
        self.assertEqual(self.programa.nombre, 'Nombre Actualizado')

    def test_horas_invalidas(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/programas/create/', {
            'nombre': 'Test',
            'nivel': Programa.Nivel.TECNICO,
            'horas_lectivas': 0,
            'horas_practicas': 0,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)


class VersionViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_vv@test.com')
        self.docente = make_docente(email='doc_vv@test.com')
        self.estudiante = make_estudiante(email='est_vv@test.com')
        self.programa = make_programa()
        self.version = make_version(programa=self.programa)

    def test_coord_lista_versiones(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/versiones/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_coord_crea_version(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/versiones/create/', {
            'programa': self.programa.pk,
            'numero': 99,
            'vigente': False,
            'fecha_inicio': '2025-01-01',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear_version(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/versiones/create/', {
            'programa': self.programa.pk,
            'numero': 98,
            'vigente': False,
            'fecha_inicio': '2025-01-01',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_estudiante_ve_solo_su_version(self):
        make_ficha_para_estudiante(self.version, self.estudiante)
        otra_version = make_version(programa=self.programa, vigente=False)
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get('/api/versiones/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [v['id'] for v in r.data['results']]
        self.assertIn(self.version.pk, ids)
        self.assertNotIn(otra_version.pk, ids)

    def test_numero_duplicado(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/versiones/create/', {
            'programa': self.programa.pk,
            'numero': self.version.numero,
            'vigente': False,
            'fecha_inicio': '2025-01-01',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)


class ModuloViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_mv@test.com')
        self.docente = make_docente(email='doc_mv@test.com')
        self.estudiante = make_estudiante(email='est_mv@test.com')
        self.version = make_version()
        self.modulo = make_modulo(version=self.version)

    def test_coord_lista_modulos(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/modulos/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_lista_modulos(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/modulos/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_coord_crea_modulo(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/modulos/create/', {
            'version': self.version.pk,
            'nombre': 'Módulo Nuevo',
            'orden': 99,
            'horas_lectivas': 80,
            'horas_practicas': 40,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear_modulo(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/modulos/create/', {
            'version': self.version.pk,
            'nombre': 'Intento',
            'orden': 98,
            'horas_lectivas': 40,
            'horas_practicas': 20,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_estudiante_solo_ve_modulos_de_su_version(self):
        make_ficha_para_estudiante(self.version, self.estudiante)
        otra_version = make_version()
        otro_modulo = make_modulo(version=otra_version)
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get('/api/modulos/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [m['id'] for m in r.data['results']]
        self.assertIn(self.modulo.pk, ids)
        self.assertNotIn(otro_modulo.pk, ids)

    def test_detail_incluye_docentes(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'/api/modulos/{self.modulo.pk}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('docentes_asignados', r.data)

    def test_not_found(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/modulos/99999/', **headers)
        self.assertEqual(r.status_code, 404)


class DocenteModuloViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_dm@test.com')
        self.docente = make_docente(email='doc_dm@test.com')
        self.modulo = make_modulo()
        self.asignacion = make_docente_modulo(
            docente=self.docente, modulo=self.modulo
        )

    def test_coord_lista_asignaciones(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/docentes-modulo/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_no_puede_listar(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/docentes-modulo/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_coord_crea_asignacion(self):
        nuevo_docente = make_docente(email='doc_nuevo_dm@test.com')
        nuevo_modulo = make_modulo()
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/docentes-modulo/create/', {
            'docente': nuevo_docente.pk,
            'modulo': nuevo_modulo.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_asignacion_duplicada(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/docentes-modulo/create/', {
            'docente': self.docente.pk,
            'modulo': self.modulo.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_coord_desactiva_asignacion(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/docentes-modulo/{self.asignacion.pk}/update/',
            {'activo': False},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.asignacion.refresh_from_db()
        self.assertFalse(self.asignacion.activo)

    def test_filtro_por_modulo(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(
            f'/api/docentes-modulo/?modulo={self.modulo.pk}',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        ids = [a['modulo'] for a in r.data['results']]
        self.assertTrue(all(m == self.modulo.pk for m in ids))