from django.test import TestCase
from rest_framework.test import APIClient
from users.tests.factories import make_coordinador, make_docente, get_auth_header


class ReporteSolicitarViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_rep@test.com')
        self.docente = make_docente(email='doc_rep@test.com')

    def test_tipo_invalido(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/reportes/solicitar/', {
            'tipo': 'invalido',
            'filtros': {},
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_docente_no_puede_solicitar(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/reportes/solicitar/', {
            'tipo': 'fichas',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_auth(self):
        r = self.client.post('/api/reportes/solicitar/', {
            'tipo': 'fichas',
        }, format='json')
        self.assertEqual(r.status_code, 401)

    def test_reporte_no_encontrado(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/reportes/99999/', **headers)
        self.assertEqual(r.status_code, 404)