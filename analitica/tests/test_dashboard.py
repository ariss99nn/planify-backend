from django.test import TestCase
from rest_framework.test import APIClient
from users.tests.factories import make_coordinador, make_docente, get_auth_header


class DashboardViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_dash@test.com')
        self.docente = make_docente(email='doc_dash@test.com')

    def test_coord_accede_dashboard(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/dashboard/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_no_accede(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/dashboard/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_auth(self):
        r = self.client.get('/api/dashboard/')
        self.assertEqual(r.status_code, 401)

    def test_sin_snapshot_responde(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/dashboard/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('mensaje', r.data)