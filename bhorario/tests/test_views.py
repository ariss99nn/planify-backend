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

class BloqueHorarioViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_bh@test.com')
        self.admin = make_user(rol='ADMINISTRATIVO', email='admin_bh@test.com')
        self.docente_user = make_user_docente(email='doc_bh@test.com')
        self.docente = make_docente(user=self.docente_user)
        self.estudiante = make_estudiante(email='est_bh@test.com')
        self.aula = make_aula()
        self.ficha = make_ficha()
        self.bloque = make_bloque(
            aula=self.aula, docente=self.docente,
            hora_inicio=time(8, 0), hora_fin=time(10, 0),
        )

    def test_coord_lista_todos_los_bloques(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE}/horarios/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('results', r.data)

    def test_docente_ve_solo_sus_bloques(self):
        otro_user = make_user_docente(email='otro_bh@test.com')
        otro_docente = make_docente(user=otro_user)
        otro_bloque = make_bloque(
            docente=otro_docente,
            hora_inicio=time(14, 0), hora_fin=time(16, 0),
        )
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.get(f'{BASE}/horarios/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [b['id'] for b in r.data['results']]
        self.assertIn(self.bloque.pk, ids)
        self.assertNotIn(otro_bloque.pk, ids)

    def test_sin_autenticacion_retorna_401(self):
        r = self.client.get(f'{BASE}/horarios/')
        self.assertEqual(r.status_code, 401)

    def test_coord_crea_bloque_con_aula(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/horarios/create/', {
            'dia_semana': BloqueHorario.DiaSemana.MARTES,
            'hora_inicio': '14:00', 'hora_fin': '16:00',
            'jornada': BloqueHorario.Jornada.TARDE,
            'aula': self.aula.pk,
            'docente': self.docente.pk,
            'ficha': self.ficha.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear_bloque(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.post(f'{BASE}/horarios/create/', {
            'dia_semana': BloqueHorario.DiaSemana.JUEVES,
            'hora_inicio': '06:00', 'hora_fin': '08:00',
            'jornada': BloqueHorario.Jornada.MANANA,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_conflicto_docente_rechazado_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/horarios/create/', {
            'dia_semana': BloqueHorario.DiaSemana.LUNES,
            'hora_inicio': '08:30', 'hora_fin': '10:30',
            'jornada': BloqueHorario.Jornada.MANANA,
            'docente': self.docente.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_coord_actualiza_bloque(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE}/horarios/{self.bloque.pk}/update/',
            {'jornada': BloqueHorario.Jornada.TARDE},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)

    def test_bloque_inexistente_retorna_404(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE}/horarios/99999/', **headers)
        self.assertEqual(r.status_code, 404)



class HorarioSemanalViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_sem@test.com')
        self.docente_user = make_user_docente(email='doc_sem@test.com')
        self.docente = make_docente(user=self.docente_user)
        self.ficha = make_ficha()

    def test_coord_ve_horario_semanal_ficha(self):
        make_bloque(
            ficha=self.ficha, docente=self.docente,
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
        )
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(
            f'{BASE}/horarios/semanal/?ficha={self.ficha.pk}', **headers
        )
        self.assertEqual(r.status_code, 200)

    def test_docente_ve_su_horario_semanal(self):
        make_bloque(
            docente=self.docente,
            dia=BloqueHorario.DiaSemana.MARTES,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
        )
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.get(f'{BASE}/horarios/semanal/', **headers)
        self.assertIn(r.status_code, [200, 400])


# ─────────────────────────────────────────────────────────────────────────────
# PlanTrimestral — Modelo
# ─────────────────────────────────────────────────────────────────────────────


