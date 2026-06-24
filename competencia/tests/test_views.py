from django.test import TestCase
from rest_framework.test import APIClient
from competencia.tests.factories import (
    make_asignatura, make_competencia, make_rap,
    make_docente_asignatura, make_ficha_para_modulo,
)
from competencia.models.asignatura_model import Asignatura
from users.tests.factories import (
    make_coordinador, make_administrativo,
    make_docente, make_estudiante, get_auth_header,
)


class AsignaturaViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_av@test.com')
        self.admin = make_administrativo(email='admin_av@test.com')
        self.docente = make_docente(email='doc_av@test.com')
        self.estudiante = make_estudiante(email='est_av@test.com')
        self.asignatura = make_asignatura()

    def test_coord_lista_todas(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/asignaturas/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_solo_ve_sus_asignaturas(self):
        make_docente_asignatura(docente=self.docente, asignatura=self.asignatura)
        otra = make_asignatura()
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/asignaturas/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [a['id'] for a in r.data['results']]
        self.assertIn(self.asignatura.pk, ids)
        self.assertNotIn(otra.pk, ids)

    def test_docente_sin_asignaciones_ve_lista_vacia(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/asignaturas/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 0)

    def test_estudiante_ve_asignaturas_de_su_ficha(self):
        make_ficha_para_modulo(self.asignatura.modulo)
        otra = make_asignatura()
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get('/api/asignaturas/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [a['id'] for a in r.data['results']]
        self.assertIn(self.asignatura.pk, ids)
        self.assertNotIn(otra.pk, ids)

    def test_coord_crea_asignatura(self):
        from programa.tests.factories import make_modulo
        modulo = make_modulo()
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/asignaturas/create/', {
            'modulo': modulo.pk,
            'nombre': 'Nueva Asignatura',
            'tipo': Asignatura.Tipo.TEORICA,
            'horas_lectivas': 60,
            'horas_practicas': 0,
            'orden': 1,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)
        self.assertIn('competencias', r.data)

    def test_docente_no_puede_crear(self):
        from programa.tests.factories import make_modulo
        modulo = make_modulo()
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/asignaturas/create/', {
            'modulo': modulo.pk,
            'nombre': 'Intento',
            'tipo': Asignatura.Tipo.PRACTICA,
            'horas_lectivas': 40,
            'horas_practicas': 20,
            'orden': 99,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_docente_no_accede_a_asignatura_ajena(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'/api/asignaturas/{self.asignatura.pk}/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_docente_con_asignacion_accede_a_detalle(self):
        make_docente_asignatura(docente=self.docente, asignatura=self.asignatura)
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'/api/asignaturas/{self.asignatura.pk}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('competencias', r.data)

    def test_not_found(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/asignaturas/99999/', **headers)
        self.assertEqual(r.status_code, 404)


class CompetenciaViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_cv@test.com')
        self.docente = make_docente(email='doc_cv@test.com')
        self.estudiante = make_estudiante(email='est_cv@test.com')
        self.asignatura = make_asignatura()
        self.competencia = make_competencia(asignatura=self.asignatura)

    def test_coord_lista_todas(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/competencias/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_solo_ve_competencias_de_sus_asignaturas(self):
        make_docente_asignatura(docente=self.docente, asignatura=self.asignatura)
        otra_comp = make_competencia()
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/competencias/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [c['id'] for c in r.data['results']]
        self.assertIn(self.competencia.pk, ids)
        self.assertNotIn(otra_comp.pk, ids)

    def test_coord_crea_competencia(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/competencias/create/', {
            'asignatura': self.asignatura.pk,
            'codigo': 'COMP-NEW',
            'nombre': 'Nueva Competencia',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)
        self.assertIn('resultados', r.data)

    def test_docente_no_puede_crear(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/competencias/create/', {
            'asignatura': self.asignatura.pk,
            'codigo': 'COMP-INT',
            'nombre': 'Intento',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_coord_actualiza_competencia(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/competencias/{self.competencia.pk}/update/',
            {'nombre': 'Nombre Actualizado'},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)

    def test_not_found(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/competencias/99999/', **headers)
        self.assertEqual(r.status_code, 404)


class RAPViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_rv@test.com')
        self.docente = make_docente(email='doc_rv@test.com')
        self.asignatura = make_asignatura()
        self.competencia = make_competencia(asignatura=self.asignatura)
        self.rap = make_rap(competencia=self.competencia)

    def test_coord_lista_todos(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/resultados/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_solo_ve_rap_de_sus_asignaturas(self):
        make_docente_asignatura(docente=self.docente, asignatura=self.asignatura)
        otro_rap = make_rap()
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/resultados/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [r_['id'] for r_ in r.data['results']]
        self.assertIn(self.rap.pk, ids)
        self.assertNotIn(otro_rap.pk, ids)

    def test_coord_crea_rap(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/resultados/create/', {
            'competencia': self.competencia.pk,
            'codigo': 'RAP-NEW',
            'descripcion': 'Aplica técnicas avanzadas.',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/resultados/create/', {
            'competencia': self.competencia.pk,
            'codigo': 'RAP-INT',
            'descripcion': 'Intento.',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_not_found(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/resultados/99999/', **headers)
        self.assertEqual(r.status_code, 404)


class DocenteAsignaturaViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_dav@test.com')
        self.docente = make_docente(email='doc_dav@test.com')
        self.otro_docente = make_docente(email='doc_dav2@test.com')
        self.asignatura = make_asignatura()
        self.asignacion = make_docente_asignatura(
            docente=self.docente, asignatura=self.asignatura
        )

    def test_coord_lista_todas(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/docentes-asignatura/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_ve_solo_sus_asignaciones(self):
        otra_asignatura = make_asignatura()
        make_docente_asignatura(
            docente=self.otro_docente, asignatura=otra_asignatura
        )
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/docentes-asignatura/', **headers)
        self.assertEqual(r.status_code, 200)
        docentes = [a['docente'] for a in r.data['results']]
        self.assertTrue(all(d == self.docente.pk for d in docentes))

    def test_coord_crea_asignacion(self):
        nueva_asignatura = make_asignatura()
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/docentes-asignatura/create/', {
            'docente': self.otro_docente.pk,
            'asignatura': nueva_asignatura.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_asignacion_duplicada(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/docentes-asignatura/create/', {
            'docente': self.docente.pk,
            'asignatura': self.asignatura.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_coord_desactiva_asignacion(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/docentes-asignatura/{self.asignacion.pk}/update/',
            {'activo': False},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.asignacion.refresh_from_db()
        self.assertFalse(self.asignacion.activo)

    def test_sin_autenticacion(self):
        r = self.client.get('/api/docentes-asignatura/')
        self.assertEqual(r.status_code, 401)

    def test_filtro_por_asignatura(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(
            f'/api/docentes-asignatura/?asignatura={self.asignatura.pk}',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        asignaturas = [a['asignatura'] for a in r.data['results']]
        self.assertTrue(all(a == self.asignatura.pk for a in asignaturas))