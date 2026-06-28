# aulas/tests/test_views.py
"""
Tests de las vistas del módulo aulas.

CORRECCIONES:
- URL base /api/ (sin /v1/).
- make_aula incluye piso=1 correctamente.
- Aula.Estado y TipoAula usan valores cortos.
- Estudiantes NO tienen acceso a aulas (CanManageAula).
"""
from django.test import TestCase
from rest_framework.test import APIClient

from users.tests.factories import (
    make_coordinador, make_docente, make_estudiante, get_auth_header,
)
from aulas.tests.factories import make_aula, make_bloque, make_equipamiento
from aulas.models.aula_model import Aula
from aulas.models.bloque_model import Bloque
from aulas.models.equipamiento_model import Equipamiento

BLOQUES = '/api/bloques'
EQUIP   = '/api/equipamiento'
AULAS   = '/api/aulas'


class BloqueViewTest(TestCase):

    def setUp(self):
        self.client  = APIClient()
        self.coord   = make_coordinador(email='coord_bl@t.com')
        self.docente = make_docente(email='doc_bl@t.com')
        self.est     = make_estudiante(email='est_bl@t.com')
        self.bloque  = make_bloque(nombre='Bloque A')

    def test_coordinador_lista_bloques(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BLOQUES}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_lista_bloques(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'{BLOQUES}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_estudiante_no_puede_listar(self):
        headers = get_auth_header(self.client, self.est)
        r = self.client.get(f'{BLOQUES}/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_autenticacion_retorna_401(self):
        self.assertEqual(self.client.get(f'{BLOQUES}/').status_code, 401)

    def test_coordinador_crea_bloque(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BLOQUES}/create/', {
            'nombre': 'Bloque Nuevo',
            'pisos': 4,
            'capacidad_maxima': 300,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post(f'{BLOQUES}/create/', {
            'nombre': 'Intento',
            'pisos': 2,
            'capacidad_maxima': 100,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_nombre_duplicado_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BLOQUES}/create/', {
            'nombre': 'Bloque A',  # ya existe
            'pisos': 2,
            'capacidad_maxima': 100,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_detalle_bloque(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BLOQUES}/{self.bloque.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_actualiza_bloque(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BLOQUES}/{self.bloque.pk}/update/',
            {'pisos': 5},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)


class EquipamientoViewTest(TestCase):

    def setUp(self):
        self.client      = APIClient()
        self.coord       = make_coordinador(email='coord_eq@t.com')
        self.docente     = make_docente(email='doc_eq@t.com')
        self.equipamiento = make_equipamiento(nombre='Proyector Test')

    def test_coordinador_lista(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{EQUIP}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_lista(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'{EQUIP}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_sin_autenticacion_retorna_401(self):
        self.assertEqual(self.client.get(f'{EQUIP}/').status_code, 401)

    def test_crea_equipamiento(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{EQUIP}/create/', {
            'nombre': 'Monitor 24"',
            'cantidad': 10,
            'estado': Equipamiento.Estado.FUNCIONAL,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post(f'{EQUIP}/create/', {
            'nombre': 'Intento',
            'cantidad': 1,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_detalle(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{EQUIP}/{self.equipamiento.pk}/', **headers)
        self.assertEqual(r.status_code, 200)


class AulaViewTest(TestCase):

    def setUp(self):
        self.client  = APIClient()
        self.coord   = make_coordinador(email='coord_au@t.com')
        self.docente = make_docente(email='doc_au@t.com')
        self.est     = make_estudiante(email='est_au@t.com')
        self.bloque  = make_bloque(nombre='Bloque Aulas Test')
        self.aula    = make_aula(bloque=self.bloque, codigo='AU101')

    def test_coordinador_lista(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{AULAS}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_lista(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'{AULAS}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_estudiante_no_puede_listar(self):
        headers = get_auth_header(self.client, self.est)
        r = self.client.get(f'{AULAS}/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_autenticacion_retorna_401(self):
        self.assertEqual(self.client.get(f'{AULAS}/').status_code, 401)

    def test_coordinador_crea_aula(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{AULAS}/create/', {
            'codigo_aula': 'AU201',
            'capacidad': 35,
            'tipo_aula': Aula.TipoAula.LABORATORIO,  # 'LAB'
            'bloque': self.bloque.pk,
            'piso': 2,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post(f'{AULAS}/create/', {
            'codigo_aula': 'AU999',
            'capacidad': 30,
            'tipo_aula': Aula.TipoAula.TEORICA,
            'bloque': self.bloque.pk,
            'piso': 1,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_piso_supera_pisos_bloque_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{AULAS}/create/', {
            'codigo_aula': 'AU-ALTO',
            'capacidad': 30,
            'tipo_aula': Aula.TipoAula.TEORICA,
            'bloque': self.bloque.pk,
            'piso': 99,  # bloque tiene 3 pisos
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_detalle_aula_incluye_equipamiento(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{AULAS}/{self.aula.pk}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('equipamiento', r.data)

    def test_actualiza_aula(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{AULAS}/{self.aula.pk}/update/',
            {'capacidad': 50},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.aula.refresh_from_db()
        self.assertEqual(self.aula.capacidad, 50)

    def test_inexistente_retorna_404(self):
        headers = get_auth_header(self.client, self.coord)
        self.assertEqual(
            self.client.get(f'{AULAS}/99999/', **headers).status_code, 404
        )


class AulaEstadoViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord  = make_coordinador(email='coord_est@t.com')
        self.est    = make_estudiante(email='est_est@t.com')
        self.aula   = make_aula(codigo='EST101')

    def test_coordinador_cambia_estado_a_mantenimiento(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{AULAS}/{self.aula.pk}/estado/',
            {'estado': Aula.Estado.MANTENIMIENTO},  # 'MANT'
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.aula.refresh_from_db()
        self.assertEqual(self.aula.estado, Aula.Estado.MANTENIMIENTO)

    def test_estudiante_no_puede_cambiar_estado(self):
        headers = get_auth_header(self.client, self.est)
        r = self.client.patch(
            f'{AULAS}/{self.aula.pk}/estado/',
            {'estado': Aula.Estado.INACTIVA},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 403)

    def test_estado_invalido_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{AULAS}/{self.aula.pk}/estado/',
            {'estado': 'INVALIDO'},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 400)