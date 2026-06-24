from datetime import date
from django.test import TestCase
from rest_framework.test import APIClient
from ficha.tests.factories import (
    make_ficha, make_ficha_estudiante, make_reasignacion,
)
from ficha.models.ficha_model import Ficha
from ficha.models.ficha_estudiante_model import FichaEstudiante
from ficha.models.ficha_historial_etapa_model import HistorialEtapa
from users.tests.factories import (
    make_coordinador, make_administrativo,
    make_docente, make_estudiante, get_auth_header,
)


class FichaListViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_flv@test.com')
        self.docente = make_docente(email='doc_flv@test.com')
        self.estudiante = make_estudiante(email='est_flv@test.com')
        self.ficha = make_ficha(jefe_grupo=self.docente)

    def test_coord_ve_todas(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/fichas/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_ve_sus_fichas(self):
        otra_ficha = make_ficha()
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/fichas/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [f['id'] for f in r.data['results']]
        self.assertIn(self.ficha.pk, ids)
        self.assertNotIn(otra_ficha.pk, ids)

    def test_estudiante_ve_su_ficha(self):
        make_ficha_estudiante(
            ficha=self.ficha, estudiante=self.estudiante, activo=True
        )
        otra_ficha = make_ficha()
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get('/api/fichas/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [f['id'] for f in r.data['results']]
        self.assertIn(self.ficha.pk, ids)
        self.assertNotIn(otra_ficha.pk, ids)

    def test_sin_autenticacion(self):
        r = self.client.get('/api/fichas/')
        self.assertEqual(r.status_code, 401)


class FichaDetailViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_fdv@test.com')
        self.docente = make_docente(email='doc_fdv@test.com')
        self.otro_docente = make_docente(email='otro_fdv@test.com')
        self.estudiante = make_estudiante(email='est_fdv@test.com')
        self.ficha = make_ficha(jefe_grupo=self.docente)

    def test_coord_ve_detalle(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'/api/fichas/{self.ficha.pk}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('historial_etapas_reciente', r.data)

    def test_docente_jefe_ve_detalle(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'/api/fichas/{self.ficha.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_no_jefe_no_ve_detalle(self):
        headers = get_auth_header(self.client, self.otro_docente)
        r = self.client.get(f'/api/fichas/{self.ficha.pk}/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_estudiante_activo_ve_detalle(self):
        make_ficha_estudiante(
            ficha=self.ficha, estudiante=self.estudiante, activo=True
        )
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'/api/fichas/{self.ficha.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_estudiante_no_activo_no_ve_detalle(self):
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'/api/fichas/{self.ficha.pk}/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_not_found(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/fichas/99999/', **headers)
        self.assertEqual(r.status_code, 404)


class FichaCreateUpdateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_fcu@test.com')
        self.docente = make_docente(email='doc_fcu@test.com')
        self.ficha = make_ficha()

    def test_coord_crea_ficha(self):
        from programa.tests.factories import make_version
        version = make_version()
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/fichas/create/', {
            'codigo_ficha': 'NUEVA-001',
            'version': version.pk,
            'jornada': Ficha.Jornada.MANANA,
            'numero_estudiantes_estimado': 25,
            'horas_semanales_objetivo': 40,
            'trimestre': 1,
            'fecha_inicio': '2024-01-01',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)
        self.assertIn('historial_etapas_reciente', r.data)

    def test_docente_no_puede_crear(self):
        from programa.tests.factories import make_version
        version = make_version()
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/fichas/create/', {
            'codigo_ficha': 'INTENTO-001',
            'version': version.pk,
            'jornada': Ficha.Jornada.MANANA,
            'numero_estudiantes_estimado': 20,
            'horas_semanales_objetivo': 40,
            'trimestre': 1,
            'fecha_inicio': '2024-01-01',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_coord_actualiza_ficha(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/fichas/{self.ficha.pk}/update/',
            {'trimestre': 3},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.ficha.refresh_from_db()
        self.assertEqual(self.ficha.trimestre, 3)


class FichaEtapaViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_etapa@test.com')
        self.docente = make_docente(email='doc_etapa@test.com')
        self.ficha = make_ficha(etapa=Ficha.Etapa.LECTIVA)

    def test_coord_cambia_etapa(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/fichas/{self.ficha.pk}/etapa/',
            {'etapa': Ficha.Etapa.PRODUCTIVA},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.ficha.refresh_from_db()
        self.assertEqual(self.ficha.etapa, Ficha.Etapa.PRODUCTIVA)

    def test_cambio_etapa_crea_historial(self):
        headers = get_auth_header(self.client, self.coord)
        self.client.patch(
            f'/api/fichas/{self.ficha.pk}/etapa/',
            {'etapa': Ficha.Etapa.PRODUCTIVA},
            format='json',
            **headers,
        )
        self.assertEqual(
            HistorialEtapa.objects.filter(ficha=self.ficha).count(), 1
        )

    def test_docente_no_puede_cambiar_etapa(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.patch(
            f'/api/fichas/{self.ficha.pk}/etapa/',
            {'etapa': Ficha.Etapa.PRODUCTIVA},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 403)


class FichaEstudianteViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_est_v@test.com')
        self.docente = make_docente(email='doc_est_v@test.com')
        self.otro_docente = make_docente(email='otro_est_v@test.com')
        self.estudiante = make_estudiante(email='est_est_v@test.com')
        self.ficha = make_ficha(jefe_grupo=self.docente)
        self.fe = make_ficha_estudiante(
            ficha=self.ficha, estudiante=self.estudiante, activo=True
        )

    def test_coord_lista_estudiantes(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(
            f'/api/fichas/{self.ficha.pk}/estudiantes/', **headers
        )
        self.assertEqual(r.status_code, 200)

    def test_docente_jefe_lista_estudiantes(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(
            f'/api/fichas/{self.ficha.pk}/estudiantes/', **headers
        )
        self.assertEqual(r.status_code, 200)

    def test_docente_no_jefe_no_puede_listar(self):
        headers = get_auth_header(self.client, self.otro_docente)
        r = self.client.get(
            f'/api/fichas/{self.ficha.pk}/estudiantes/', **headers
        )
        self.assertEqual(r.status_code, 403)

    def test_estudiante_no_puede_listar(self):
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(
            f'/api/fichas/{self.ficha.pk}/estudiantes/', **headers
        )
        self.assertEqual(r.status_code, 403)

    def test_coord_agrega_estudiante(self):
        nuevo_estudiante = make_estudiante(email='nuevo_est@test.com')
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(
            f'/api/fichas/{self.ficha.pk}/estudiantes/add/',
            {'estudiante': nuevo_estudiante.pk, 'es_cadena': False},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 201)

    def test_coord_desactiva_estudiante(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/fichas/{self.ficha.pk}/estudiantes/{self.fe.pk}/',
            {
                'activo': False,
                'fecha_retiro': '2024-06-01',
                'motivo_retiro': FichaEstudiante.MotivoRetiro.DESERCION,
            },
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.fe.refresh_from_db()
        self.assertFalse(self.fe.activo)


class ReasignacionViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_reas_v@test.com')
        self.docente = make_docente(email='doc_reas_v@test.com')
        self.estudiante = make_estudiante(email='est_reas_v@test.com')
        self.ficha_origen = make_ficha()
        self.ficha_destino = make_ficha()
        self.fe = make_ficha_estudiante(
            ficha=self.ficha_origen, estudiante=self.estudiante, activo=True
        )

    def test_coord_lista_reasignaciones(self):
        make_reasignacion(
            estudiante=self.estudiante,
            ficha_origen=self.ficha_origen,
            ficha_destino=self.ficha_destino,
        )
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/fichas/reasignaciones/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_no_puede_listar(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/fichas/reasignaciones/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_coord_crea_reasignacion(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/fichas/reasignaciones/create/', {
            'estudiante': self.estudiante.pk,
            'ficha_origen': self.ficha_origen.pk,
            'ficha_destino': self.ficha_destino.pk,
            'motivo': 'Cambio de jornada por trabajo',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)
        self.fe.refresh_from_db()
        self.assertFalse(self.fe.activo)
        self.assertEqual(
            self.fe.motivo_retiro, FichaEstudiante.MotivoRetiro.REASIGNADO
        )

    def test_reasignacion_origen_igual_destino(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/fichas/reasignaciones/create/', {
            'estudiante': self.estudiante.pk,
            'ficha_origen': self.ficha_origen.pk,
            'ficha_destino': self.ficha_origen.pk,
            'motivo': 'Misma ficha',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)


class HistorialEtapaViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_hist@test.com')
        self.docente = make_docente(email='doc_hist@test.com')
        self.ficha = make_ficha(etapa=Ficha.Etapa.LECTIVA)

    def test_coord_lista_historial(self):
        self.ficha.etapa = Ficha.Etapa.PRODUCTIVA
        self.ficha.save()
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/fichas/historial/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_no_puede_listar(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/fichas/historial/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_filtro_por_ficha(self):
        self.ficha.etapa = Ficha.Etapa.PRODUCTIVA
        self.ficha.save()
        otra_ficha = make_ficha(etapa=Ficha.Etapa.LECTIVA)
        otra_ficha.etapa = Ficha.Etapa.PRODUCTIVA
        otra_ficha.save()
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(
            f'/api/fichas/historial/?ficha={self.ficha.pk}', **headers
        )
        self.assertEqual(r.status_code, 200)
        fichas = [h['ficha'] for h in r.data['results']]
        self.assertTrue(all(f == self.ficha.pk for f in fichas))