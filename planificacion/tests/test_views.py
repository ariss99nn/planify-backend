from django.test import TestCase
from rest_framework.test import APIClient
from .factories import make_plan, make_item
from users.tests.factories import (
    make_coordinador, make_administrativo,
    make_docente, make_estudiante, get_auth_header,
)
from ficha.tests.factories import make_ficha
from competencia.tests.factories import make_competencia
from docentes.tests.factories import make_docente as make_docente_perfil


class PlanTrimestralViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_pv@test.com')
        self.admin = make_administrativo(email='admin_pv@test.com')
        self.docente_user = make_docente(email='doc_pv@test.com')
        self.estudiante = make_estudiante(email='est_pv@test.com')
        self.ficha = make_ficha()
        self.plan = make_plan(ficha=self.ficha)

    def test_coord_lista_planes(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/planes/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_estudiante_no_puede_listar(self):
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get('/api/planes/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 0)

    def test_coord_crea_plan(self):
        ficha2 = make_ficha()
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/planes/create/', {
            'ficha': ficha2.pk,
            'trimestre': 1,
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-04-30',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.post('/api/planes/create/', {
            'ficha': self.ficha.pk,
            'trimestre': 2,
            'fecha_inicio': '2024-05-01',
            'fecha_fin': '2024-08-31',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_aprobar_plan_sin_items_falla(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/planes/{self.plan.pk}/aprobar/',
            {'aprobado': True},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 400)

    def test_aprobar_plan_con_items(self):
        make_item(plan=self.plan)
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/planes/{self.plan.pk}/aprobar/',
            {'aprobado': True},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.plan.refresh_from_db()
        self.assertTrue(self.plan.estado == self.plan.EstadoPlan.APROBADO)

    def test_admin_no_puede_aprobar(self):
        make_item(plan=self.plan)
        headers = get_auth_header(self.client, self.admin)
        r = self.client.patch(
            f'/api/planes/{self.plan.pk}/aprobar/',
            {'aprobado': True},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 403)

    def test_not_found(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/planes/99999/', **headers)
        self.assertEqual(r.status_code, 404)

    def test_generar_horario_plan_no_aprobado(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(
            f'/api/planes/{self.plan.pk}/generar-horario/',
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 400)