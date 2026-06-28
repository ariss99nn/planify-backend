from datetime import date, time
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from users.tests.factories import (
    make_coordinador, make_docente as make_user_docente,
    make_estudiante, make_user, get_auth_header,
)
from docentes.tests.factories import make_docente, make_docente_user, make_docente_inactivo
from bhorario.tests.factories import make_bloque
from planificacion.tests.factories import make_plan, make_item
from ficha.tests.factories import make_ficha
from competencia.tests.factories import make_competencia, make_asignatura
from aulas.tests import make_aula

from bhorario.models.bloque_horario_model import BloqueHorario
from bhorario.services.bloque_service import BloqueHorarioService, ColisionError
from planificacion.models.plan_trimestral_model import PlanTrimestral
from docentes.models.docente_model import Docente

BASE = '/api/v1'

class DocenteListViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_dl@test.com')
        self.admin = make_user(rol='ADMINISTRATIVO', email='admin_dl@test.com')
        self.docente_user = make_user_docente(email='doc_dl@test.com')
        self.estudiante = make_estudiante(email='est_dl@test.com')
        make_docente()
        make_docente()

    def test_coordinador_puede_listar(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE}/docentes/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('results', r.data)

    def test_administrativo_puede_listar(self):
        headers = get_auth_header(self.client, self.admin)
        r = self.client.get(f'{BASE}/docentes/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_no_puede_listar(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.get(f'{BASE}/docentes/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_estudiante_no_puede_listar(self):
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'{BASE}/docentes/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_autenticacion_retorna_401(self):
        r = self.client.get(f'{BASE}/docentes/')
        self.assertEqual(r.status_code, 401)



class DocenteCreateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_dc@test.com')
        self.docente_user = make_user_docente(email='doc_dc@test.com')

    def test_coordinador_crea_docente_exitoso(self):
        user = make_docente_user(email='nuevo_dc@test.com')
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/docentes/create/', {
            'user_id': user.pk,
            'especialidad': 'Historia',
            'horas_max_semanales': 18,
            'estado': True,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear(self):
        user = make_docente_user(email='nuevo_dc2@test.com')
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.post(f'{BASE}/docentes/create/', {
            'user_id': user.pk, 'especialidad': 'Arte', 'horas_max_semanales': 10,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_user_con_perfil_existente_retorna_400(self):
        user = make_docente_user(email='yaexiste@test.com')
        make_docente(user=user)
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/docentes/create/', {
            'user_id': user.pk, 'especialidad': 'Física', 'horas_max_semanales': 20,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_horas_cero_invalidas(self):
        user = make_docente_user(email='horas_dc@test.com')
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/docentes/create/', {
            'user_id': user.pk, 'especialidad': 'Música', 'horas_max_semanales': 0,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)



class DisponibilidadViewTest(TestCase):
    """Tests del endpoint de disponibilidad de docentes."""

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_disp@test.com')
        self.docente_user = make_user_docente(email='doc_disp@test.com')
        self.docente = make_docente(user=self.docente_user)

    def test_docente_puede_crear_disponibilidad(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.post(f'{BASE}/docentes/{self.docente.pk}/disponibilidad/', {
            'dia_semana': BloqueHorario.DiaSemana.LUNES,
            'hora_inicio': '06:00', 'hora_fin': '08:00',
            'disponible': False,
            'tipo_restriccion': 'PERMANENTE',
        }, format='json', **headers)
        self.assertIn(r.status_code, [200, 201])

    def test_coord_puede_ver_disponibilidad(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(
            f'{BASE}/docentes/{self.docente.pk}/disponibilidad/', **headers
        )
        self.assertEqual(r.status_code, 200)


# ─────────────────────────────────────────────────────────────────────────────
# Alertas — Señales, Modelo y Vistas
# ─────────────────────────────────────────────────────────────────────────────


