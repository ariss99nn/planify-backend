from django.test import TestCase
from rest_framework.test import APIClient
from users.tests.factories import make_coordinador, make_docente, get_auth_header


class ExportacionViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_exp@test.com')
        self.docente = make_docente(email='doc_exp@test.com')

    def test_exportar_fichas_csv(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/exportar/', {
            'modulo': 'fichas',
            'formato': 'csv',
            'filtros': {},
        }, format='json', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('text/csv', r['Content-Type'])

    def test_exportar_docentes_excel(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/exportar/', {
            'modulo': 'docentes',
            'formato': 'excel',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('spreadsheetml', r['Content-Type'])

    def test_modulo_invalido(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/exportar/', {
            'modulo': 'invalido',
            'formato': 'csv',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_docente_no_puede_exportar(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/exportar/', {
            'modulo': 'fichas',
            'formato': 'csv',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_auth(self):
        r = self.client.post('/api/exportar/', {
            'modulo': 'fichas',
            'formato': 'csv',
        }, format='json')
        self.assertEqual(r.status_code, 401)