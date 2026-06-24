from django.test import TestCase
from rest_framework.test import APIClient
from aulas.tests.factories import make_bloque, make_equipamiento, make_aula
from aulas.models.aula_model import Aula
from aulas.models.equipamiento_model import Equipamiento
from users.tests.factories import (
    make_coordinador, make_administrativo,
    make_docente, make_estudiante, get_auth_header,
)


class BloqueViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_bloque@test.com')
        self.docente = make_docente(email='doc_bloque@test.com')
        self.estudiante = make_estudiante(email='est_bloque@test.com')
        self.bloque = make_bloque(nombre='Bloque Vista')

    def test_list_autenticado(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/bloques/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_list_docente_puede_ver(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get('/api/bloques/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_list_sin_auth(self):
        r = self.client.get('/api/bloques/')
        self.assertEqual(r.status_code, 401)

    def test_detail(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'/api/bloques/{self.bloque.pk}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('total_aulas', r.data)

    def test_create_coord(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/bloques/create/', {
            'nombre': 'Bloque Nuevo',
            'pisos': 2,
            'capacidad_maxima': 150,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_create_docente_forbidden(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/bloques/create/', {
            'nombre': 'Intento',
            'pisos': 1,
            'capacidad_maxima': 50,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_update_coord(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/bloques/{self.bloque.pk}/update/',
            {'pisos': 5},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.bloque.refresh_from_db()
        self.assertEqual(self.bloque.pisos, 5)

    def test_not_found(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/bloques/99999/', **headers)
        self.assertEqual(r.status_code, 404)


class EquipamientoViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_equip_v@test.com')
        self.docente = make_docente(email='doc_equip_v@test.com')
        self.equip = make_equipamiento(nombre='Monitor Vista')

    def test_list_todos_ven(self):
        for factory, email in [
            (make_docente, 'dv1@test.com'),
            (make_estudiante, 'ev1@test.com'),
        ]:
            user = factory(email=email)
            headers = get_auth_header(self.client, user)
            r = self.client.get('/api/equipamiento/', **headers)
            self.assertEqual(r.status_code, 200)

    def test_create_coord(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/equipamiento/create/', {
            'nombre': 'Teclado Nuevo',
            'cantidad': 20,
            'estado': Equipamiento.Estado.FUNCIONAL,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_create_docente_forbidden(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/equipamiento/create/', {
            'nombre': 'Intento',
            'cantidad': 1,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_update_estado(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/equipamiento/{self.equip.pk}/update/',
            {'estado': Equipamiento.Estado.DAÑADO},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.equip.refresh_from_db()
        self.assertEqual(self.equip.estado, Equipamiento.Estado.DAÑADO)

    def test_not_found(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/equipamiento/99999/', **headers)
        self.assertEqual(r.status_code, 404)


class AulaViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_aula_v@test.com')
        self.admin = make_administrativo(email='admin_aula_v@test.com')
        self.docente = make_docente(email='doc_aula_v@test.com')
        self.estudiante = make_estudiante(email='est_aula_v@test.com')
        self.bloque = make_bloque(nombre='Bloque Aula V')
        self.aula = make_aula(bloque=self.bloque, codigo='V101')

    def test_list_todos_ven(self):
        for factory, email in [
            (make_docente, 'dv2@test.com'),
            (make_estudiante, 'ev2@test.com'),
        ]:
            user = factory(email=email)
            headers = get_auth_header(self.client, user)
            r = self.client.get('/api/aulas/', **headers)
            self.assertEqual(r.status_code, 200)

    def test_list_sin_auth(self):
        r = self.client.get('/api/aulas/')
        self.assertEqual(r.status_code, 401)

    def test_detail_todos_ven(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.get(f'/api/aulas/{self.aula.pk}/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('bloque', r.data)
        self.assertIn('equipamiento', r.data)

    def test_create_coord(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/aulas/create/', {
            'codigo_aula': 'V201',
            'capacidad': 35,
            'tipo_aula': Aula.TipoAula.LABORATORIO,
            'bloque': self.bloque.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['codigo_aula'], 'V201')

    def test_create_docente_forbidden(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.post('/api/aulas/create/', {
            'codigo_aula': 'V999',
            'capacidad': 30,
            'tipo_aula': Aula.TipoAula.TEORICA,
            'bloque': self.bloque.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_create_estudiante_forbidden(self):
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.post('/api/aulas/create/', {
            'codigo_aula': 'V998',
            'capacidad': 30,
            'tipo_aula': Aula.TipoAula.TEORICA,
            'bloque': self.bloque.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_update_coord(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/aulas/{self.aula.pk}/update/',
            {'capacidad': 50},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.aula.refresh_from_db()
        self.assertEqual(self.aula.capacidad, 50)

    def test_update_docente_forbidden(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.patch(
            f'/api/aulas/{self.aula.pk}/update/',
            {'capacidad': 50},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 403)

    def test_not_found(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/aulas/99999/', **headers)
        self.assertEqual(r.status_code, 404)


class AulaEstadoViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_estado@test.com')
        self.admin = make_administrativo(email='admin_estado@test.com')
        self.docente = make_docente(email='doc_estado@test.com')
        self.estudiante = make_estudiante(email='est_estado@test.com')
        self.bloque = make_bloque(nombre='Bloque Estado')
        self.aula = make_aula(bloque=self.bloque, codigo='E101')

    def test_coord_cambia_estado(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/aulas/{self.aula.pk}/estado/',
            {'estado': Aula.Estado.MANTENIMIENTO},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.aula.refresh_from_db()
        self.assertEqual(self.aula.estado, Aula.Estado.MANTENIMIENTO)

    def test_admin_cambia_estado(self):
        headers = get_auth_header(self.client, self.admin)
        r = self.client.patch(
            f'/api/aulas/{self.aula.pk}/estado/',
            {'estado': Aula.Estado.INACTIVA},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)

    def test_docente_puede_cambiar_estado(self):
        headers = get_auth_header(self.client, self.docente)
        r = self.client.patch(
            f'/api/aulas/{self.aula.pk}/estado/',
            {'estado': Aula.Estado.MANTENIMIENTO},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.aula.refresh_from_db()
        self.assertEqual(self.aula.estado, Aula.Estado.MANTENIMIENTO)

    def test_estudiante_no_puede_cambiar_estado(self):
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.patch(
            f'/api/aulas/{self.aula.pk}/estado/',
            {'estado': Aula.Estado.INACTIVA},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 403)

    def test_estado_invalido(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/aulas/{self.aula.pk}/estado/',
            {'estado': 'INVALIDO'},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 400)

    def test_sin_autenticacion(self):
        r = self.client.patch(
            f'/api/aulas/{self.aula.pk}/estado/',
            {'estado': Aula.Estado.MANTENIMIENTO},
            format='json',
        )
        self.assertEqual(r.status_code, 401)