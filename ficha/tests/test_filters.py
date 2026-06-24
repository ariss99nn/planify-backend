from django.test import TestCase
from rest_framework.test import APIClient
from ficha.tests.factories import make_ficha, make_ficha_estudiante
from ficha.models.ficha_model import Ficha
from ficha.models.ficha_estudiante_model import FichaEstudiante
from users.tests.factories import make_coordinador, make_estudiante, get_auth_header


class FichaFilterTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_ff@test.com')
        self.headers = get_auth_header(self.client, self.coord)

        self.f1 = make_ficha(
            jornada=Ficha.Jornada.MANANA,
            etapa=Ficha.Etapa.LECTIVA,
            estado=True,
        )
        self.f2 = make_ficha(
            jornada=Ficha.Jornada.NOCHE,
            etapa=Ficha.Etapa.PRODUCTIVA,
            estado=False,
        )

    def test_filtro_etapa(self):
        r = self.client.get(
            f'/api/fichas/?etapa={Ficha.Etapa.LECTIVA}', **self.headers
        )
        self.assertEqual(r.status_code, 200)
        etapas = [f['etapa'] for f in r.data['results']]
        self.assertTrue(all(e == Ficha.Etapa.LECTIVA for e in etapas))

    def test_filtro_jornada(self):
        r = self.client.get(
            f'/api/fichas/?jornada={Ficha.Jornada.NOCHE}', **self.headers
        )
        self.assertEqual(r.status_code, 200)
        jornadas = [f['jornada'] for f in r.data['results']]
        self.assertTrue(all(j == Ficha.Jornada.NOCHE for j in jornadas))

    def test_filtro_estado(self):
        r = self.client.get('/api/fichas/?estado=false', **self.headers)
        self.assertEqual(r.status_code, 200)
        estados = [f['estado'] for f in r.data['results']]
        self.assertTrue(all(e is False for e in estados))

    def test_search_por_codigo(self):
        r = self.client.get(
            f'/api/fichas/?search={self.f1.codigo_ficha}', **self.headers
        )
        self.assertEqual(r.status_code, 200)
        codigos = [f['codigo_ficha'] for f in r.data['results']]
        self.assertIn(self.f1.codigo_ficha, codigos)

    def test_paginacion_estructura(self):
        r = self.client.get('/api/fichas/', **self.headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('count', r.data)
        self.assertIn('results', r.data)

    def test_page_size(self):
        r = self.client.get('/api/fichas/?page_size=1', **self.headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

    def test_filtro_programa(self):
        r = self.client.get(
            f'/api/fichas/?programa={self.f1.version.programa.pk}',
            **self.headers,
        )
        self.assertEqual(r.status_code, 200)
        ids = [f['id'] for f in r.data['results']]
        self.assertIn(self.f1.pk, ids)

    def test_filtro_motivo_retiro_estudiante(self):
        estudiante = make_estudiante(email='est_mr@test.com')
        fe = make_ficha_estudiante(
            ficha=self.f1, estudiante=estudiante, activo=False
        )
        from datetime import date
        fe.activo = False
        fe.fecha_retiro = date(2024, 6, 1)
        fe.motivo_retiro = FichaEstudiante.MotivoRetiro.DESERCION
        fe.save()
        r = self.client.get(
            f'/api/fichas/{self.f1.pk}/estudiantes/'
            f'?motivo_retiro={FichaEstudiante.MotivoRetiro.DESERCION}',
            **self.headers,
        )
        self.assertEqual(r.status_code, 200)