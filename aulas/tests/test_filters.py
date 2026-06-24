from django.test import TestCase
from rest_framework.test import APIClient
from aulas.tests.factories import make_bloque, make_equipamiento, make_aula
from aulas.models.aula_model import Aula
from aulas.models.equipamiento_model import Equipamiento
from users.tests.factories import make_coordinador, get_auth_header


class AulaFilterTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_filter@test.com')
        self.headers = get_auth_header(self.client, self.coord)

        self.bloque_a = make_bloque(nombre='Bloque Alpha')
        self.bloque_b = make_bloque(nombre='Bloque Beta')

        self.aula1 = make_aula(
            bloque=self.bloque_a, codigo='F101',
            tipo=Aula.TipoAula.LABORATORIO, capacidad=20,
        )
        self.aula2 = make_aula(
            bloque=self.bloque_b, codigo='F102',
            tipo=Aula.TipoAula.TEORICA, capacidad=40,
            estado=Aula.Estado.MANTENIMIENTO,
        )
        self.aula3 = make_aula(
            bloque=self.bloque_a, codigo='F103',
            tipo=Aula.TipoAula.SISTEMAS, capacidad=25,
        )

    def test_search_por_codigo(self):
        r = self.client.get('/api/aulas/?search=F101', **self.headers)
        self.assertEqual(r.status_code, 200)
        codigos = [a['codigo_aula'] for a in r.data['results']]
        self.assertIn('F101', codigos)
        self.assertNotIn('F102', codigos)

    def test_filtro_estado(self):
        r = self.client.get(
            f'/api/aulas/?estado={Aula.Estado.MANTENIMIENTO}', **self.headers
        )
        self.assertEqual(r.status_code, 200)
        estados = [a['estado'] for a in r.data['results']]
        self.assertTrue(all(e == Aula.Estado.MANTENIMIENTO for e in estados))

    def test_filtro_tipo_aula(self):
        r = self.client.get(
            f'/api/aulas/?tipo_aula={Aula.TipoAula.LABORATORIO}', **self.headers
        )
        self.assertEqual(r.status_code, 200)
        tipos = [a['tipo_aula'] for a in r.data['results']]
        self.assertTrue(all(t == Aula.TipoAula.LABORATORIO for t in tipos))

    def test_filtro_capacidad_min(self):
        r = self.client.get('/api/aulas/?capacidad_min=35', **self.headers)
        self.assertEqual(r.status_code, 200)
        capacidades = [a['capacidad'] for a in r.data['results']]
        self.assertTrue(all(c >= 35 for c in capacidades))

    def test_paginacion_estructura(self):
        r = self.client.get('/api/aulas/', **self.headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('count', r.data)
        self.assertIn('results', r.data)

    def test_page_size(self):
        r = self.client.get('/api/aulas/?page_size=1', **self.headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)


class EquipamientoFilterTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_equip@test.com')
        self.headers = get_auth_header(self.client, self.coord)

        make_equipamiento(
            nombre='Proyector Epson',
            estado=Equipamiento.Estado.FUNCIONAL,
        )
        make_equipamiento(
            nombre='Computador HP',
            estado=Equipamiento.Estado.DAÑADO,
        )

    def test_search_por_nombre(self):
        r = self.client.get('/api/equipamiento/?search=Epson', **self.headers)
        self.assertEqual(r.status_code, 200)
        nombres = [e['nombre'] for e in r.data['results']]
        self.assertIn('Proyector Epson', nombres)

    def test_filtro_estado_equipamiento(self):
        r = self.client.get(
            f'/api/equipamiento/?estado={Equipamiento.Estado.DAÑADO}',
            **self.headers,
        )
        self.assertEqual(r.status_code, 200)
        estados = [e['estado'] for e in r.data['results']]
        self.assertTrue(all(e == Equipamiento.Estado.DAÑADO for e in estados))

    def test_paginacion_equipamiento(self):
        r = self.client.get('/api/equipamiento/', **self.headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('count', r.data)
        self.assertIn('results', r.data)