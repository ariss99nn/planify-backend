from django.test import TestCase
from rest_framework.test import APIClient
from docentes.tests.factories import make_docente, make_docente_user, make_docente_inactivo
from docentes.models.docente_model import Docente
from users.tests.factories import (
    make_coordinador, make_administrativo,
    make_docente as make_user_docente,
    make_estudiante, get_auth_header,
)


class DocenteListViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord@test.com')
        self.admin = make_administrativo(email='admin@test.com')
        self.docente_user = make_user_docente(email='doc@test.com')
        self.estudiante = make_estudiante(email='est@test.com')
        make_docente()
        make_docente()

    def test_coordinador_puede_listar(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.get('/api/docentes/', **headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)

    def test_administrativo_puede_listar(self):
        headers = get_auth_header(self.client, self.admin)
        response = self.client.get('/api/docentes/', **headers)
        self.assertEqual(response.status_code, 200)

    def test_docente_no_puede_listar(self):
        headers = get_auth_header(self.client, self.docente_user)
        response = self.client.get('/api/docentes/', **headers)
        self.assertEqual(response.status_code, 403)

    def test_estudiante_no_puede_listar(self):
        headers = get_auth_header(self.client, self.estudiante)
        response = self.client.get('/api/docentes/', **headers)
        self.assertEqual(response.status_code, 403)

    def test_sin_autenticacion(self):
        response = self.client.get('/api/docentes/')
        self.assertEqual(response.status_code, 401)


class DocenteDetailViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord2@test.com')
        self.docente_user = make_user_docente(email='doc2@test.com')
        self.docente = make_docente()

    def test_coordinador_ve_detalle(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.get(f'/api/docentes/{self.docente.pk}/', **headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.data)
        self.assertIn('especialidad', response.data)

    def test_docente_no_puede_ver_detalle(self):
        headers = get_auth_header(self.client, self.docente_user)
        response = self.client.get(f'/api/docentes/{self.docente.pk}/', **headers)
        self.assertEqual(response.status_code, 403)

    def test_no_encontrado(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.get('/api/docentes/99999/', **headers)
        self.assertEqual(response.status_code, 404)


class DocenteCreateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord3@test.com')
        self.docente_user = make_user_docente(email='doc3@test.com')

    def test_coordinador_crea_docente(self):
        user = make_docente_user(email='nuevo@test.com')
        headers = get_auth_header(self.client, self.coord)
        response = self.client.post('/api/docentes/create/', {
            'user_id': user.pk,
            'especialidad': 'Historia',
            'horas_max_semanales': 18,
            'estado': True,
        }, format='json', **headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['especialidad'], 'Historia')
        self.assertIn('user', response.data)

    def test_docente_no_puede_crear(self):
        user = make_docente_user(email='nuevo2@test.com')
        headers = get_auth_header(self.client, self.docente_user)
        response = self.client.post('/api/docentes/create/', {
            'user_id': user.pk,
            'especialidad': 'Arte',
            'horas_max_semanales': 10,
        }, format='json', **headers)
        self.assertEqual(response.status_code, 403)

    def test_user_ya_tiene_perfil(self):
        user = make_docente_user(email='yaexiste2@test.com')
        make_docente(user=user)
        headers = get_auth_header(self.client, self.coord)
        response = self.client.post('/api/docentes/create/', {
            'user_id': user.pk,
            'especialidad': 'Física',
            'horas_max_semanales': 20,
        }, format='json', **headers)
        self.assertEqual(response.status_code, 400)

    def test_horas_invalidas(self):
        user = make_docente_user(email='horas@test.com')
        headers = get_auth_header(self.client, self.coord)
        response = self.client.post('/api/docentes/create/', {
            'user_id': user.pk,
            'especialidad': 'Música',
            'horas_max_semanales': 0,
        }, format='json', **headers)
        self.assertEqual(response.status_code, 400)

    def test_sin_autenticacion(self):
        user = make_docente_user(email='nuevo3@test.com')
        response = self.client.post('/api/docentes/create/', {
            'user_id': user.pk,
            'especialidad': 'Arte',
            'horas_max_semanales': 10,
        }, format='json')
        self.assertEqual(response.status_code, 401)


class DocenteUpdateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord4@test.com')
        self.docente_user = make_user_docente(email='doc4@test.com')
        self.docente = make_docente(especialidad='Inglés', horas=15)

    def test_coordinador_actualiza(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            f'/api/docentes/{self.docente.pk}/update/',
            {'especialidad': 'Inglés Avanzado'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.docente.refresh_from_db()
        self.assertEqual(self.docente.especialidad, 'Inglés Avanzado')

    def test_horas_sobre_40_rechazado(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            f'/api/docentes/{self.docente.pk}/update/',
            {'horas_max_semanales': 41},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_docente_no_puede_actualizar(self):
        headers = get_auth_header(self.client, self.docente_user)
        response = self.client.patch(
            f'/api/docentes/{self.docente.pk}/update/',
            {'especialidad': 'Arte'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_no_encontrado(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            '/api/docentes/99999/update/',
            {'especialidad': 'Arte'},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 404)


class DocenteDeactivateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord5@test.com')
        self.docente_user = make_user_docente(email='doc5@test.com')
        self.docente = make_docente()

    def test_coordinador_desactiva(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            f'/api/docentes/{self.docente.pk}/deactivate/',
            {'confirmacion': True},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 200)

        self.docente.refresh_from_db()
        self.docente.user.refresh_from_db()
        self.assertFalse(self.docente.estado)
        self.assertFalse(self.docente.user.estado)

    def test_registro_persiste_historico(self):
        pk = self.docente.pk
        headers = get_auth_header(self.client, self.coord)
        self.client.patch(
            f'/api/docentes/{self.docente.pk}/deactivate/',
            {'confirmacion': True},
            format='json',
            **headers,
        )
        self.assertTrue(Docente.objects.filter(pk=pk).exists())

    def test_sin_confirmacion_falla(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            f'/api/docentes/{self.docente.pk}/deactivate/',
            {'confirmacion': False},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 400)
        self.docente.refresh_from_db()
        self.assertTrue(self.docente.estado)

    def test_docente_no_puede_desactivar(self):
        headers = get_auth_header(self.client, self.docente_user)
        response = self.client.patch(
            f'/api/docentes/{self.docente.pk}/deactivate/',
            {'confirmacion': True},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_no_encontrado(self):
        headers = get_auth_header(self.client, self.coord)
        response = self.client.patch(
            '/api/docentes/99999/deactivate/',
            {'confirmacion': True},
            format='json',
            **headers,
        )
        self.assertEqual(response.status_code, 404)