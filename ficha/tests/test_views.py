from datetime import date, time
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse

from users.tests.factories import (
    make_coordinador, make_docente as make_user_docente,
    make_estudiante, make_user, get_auth_header,
)
from docentes.tests.factories import make_docente, make_docente_user
from ficha.tests.factories import make_ficha, make_ficha_estudiante, make_reasignacion
from programa.tests.factories import make_programa, make_version, make_modulo, make_docente_modulo
from competencia.tests.factories import make_asignatura, make_competencia, make_rap, make_docente_asignatura
from aulas.tests import make_aula, make_bloque as make_bloque_aulas, make_equipamiento
from bhorario.tests.factories import make_bloque

from ficha.models.ficha_model import Ficha
from ficha.models.ficha_estudiante_model import FichaEstudiante
from ficha.models.ficha_historial_etapa_model import HistorialEtapa
from aulas.models.aula_model import Aula
from aulas.models.bloque_model import Bloque
from aulas.models.equipamiento_model import Equipamiento
from competencia.models.asignatura_model import Asignatura
from competencia.models.competencia_model import Competencia
from programa.models.programa_model import Programa
from programa.models.modulo_model import Modulo

BASE = '/api/v1'

class FichaListViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_fl@t.com')
        self.docente_user = make_user_docente(email='doc_fl@t.com')
        self.estudiante = make_estudiante(email='est_fl@t.com')
        self.ficha = make_ficha(jefe_grupo=self.docente_user)

    def test_coord_ve_todas(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE}/fichas/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_ve_sus_fichas_como_jefe(self):
        otra = make_ficha()
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.get(f'{BASE}/fichas/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [f['id'] for f in r.data['results']]
        self.assertIn(self.ficha.pk, ids)
        self.assertNotIn(otra.pk, ids)

    def test_estudiante_ve_su_ficha(self):
        make_ficha_estudiante(ficha=self.ficha, estudiante=self.estudiante, activo=True)
        otra = make_ficha()
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'{BASE}/fichas/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [f['id'] for f in r.data['results']]
        self.assertIn(self.ficha.pk, ids)
        self.assertNotIn(otra.pk, ids)

    def test_sin_autenticacion_retorna_401(self):
        self.assertEqual(self.client.get(f'{BASE}/fichas/').status_code, 401)



class FichaDetailViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_fd@t.com')
        self.docente_user = make_user_docente(email='doc_fd@t.com')
        self.otro_docente = make_user_docente(email='otro_fd@t.com')
        self.estudiante = make_estudiante(email='est_fd@t.com')
        self.ficha = make_ficha(jefe_grupo=self.docente_user)

    def test_coord_ve_detalle(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE}/fichas/{self.ficha.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_jefe_ve_detalle(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.get(f'{BASE}/fichas/{self.ficha.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_no_jefe_retorna_403(self):
        headers = get_auth_header(self.client, self.otro_docente)
        r = self.client.get(f'{BASE}/fichas/{self.ficha.pk}/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_estudiante_activo_ve_detalle(self):
        make_ficha_estudiante(ficha=self.ficha, estudiante=self.estudiante, activo=True)
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'{BASE}/fichas/{self.ficha.pk}/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_estudiante_sin_matricula_retorna_403(self):
        headers = get_auth_header(self.client, self.estudiante)
        r = self.client.get(f'{BASE}/fichas/{self.ficha.pk}/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_inexistente_retorna_404(self):
        headers = get_auth_header(self.client, self.coord)
        self.assertEqual(
            self.client.get(f'{BASE}/fichas/99999/', **headers).status_code, 404
        )



class FichaEtapaViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_et@t.com')
        self.docente_user = make_user_docente(email='doc_et@t.com')
        self.ficha = make_ficha(etapa=Ficha.Etapa.LECTIVA)

    def test_coord_cambia_etapa(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE}/fichas/{self.ficha.pk}/etapa/',
            {'etapa': Ficha.Etapa.PRODUCTIVA},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.ficha.refresh_from_db()
        self.assertEqual(self.ficha.etapa, Ficha.Etapa.PRODUCTIVA)

    def test_cambio_etapa_crea_historial(self):
        headers = get_auth_header(self.client, self.coord)
        self.client.patch(
            f'{BASE}/fichas/{self.ficha.pk}/etapa/',
            {'etapa': Ficha.Etapa.PRODUCTIVA},
            format='json', **headers,
        )
        self.assertEqual(HistorialEtapa.objects.filter(ficha=self.ficha).count(), 1)

    def test_docente_no_puede_cambiar_etapa(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.patch(
            f'{BASE}/fichas/{self.ficha.pk}/etapa/',
            {'etapa': Ficha.Etapa.PRODUCTIVA},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 403)



class FichaEstudianteViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_fe@t.com')
        self.docente_user = make_user_docente(email='doc_fe@t.com')
        self.otro_docente = make_user_docente(email='otro_fe@t.com')
        self.estudiante = make_estudiante(email='est_fe@t.com')
        self.ficha = make_ficha(jefe_grupo=self.docente_user)
        self.fe = make_ficha_estudiante(
            ficha=self.ficha, estudiante=self.estudiante, activo=True
        )

    def test_coord_lista_estudiantes(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE}/fichas/{self.ficha.pk}/estudiantes/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_jefe_lista_estudiantes(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.get(f'{BASE}/fichas/{self.ficha.pk}/estudiantes/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_no_jefe_retorna_403(self):
        headers = get_auth_header(self.client, self.otro_docente)
        r = self.client.get(f'{BASE}/fichas/{self.ficha.pk}/estudiantes/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_coord_agrega_estudiante(self):
        nuevo = make_estudiante(email='nuevo_fe@t.com')
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(
            f'{BASE}/fichas/{self.ficha.pk}/estudiantes/add/',
            {'estudiante': nuevo.pk, 'es_cadena': False},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 201)

    def test_coord_desactiva_estudiante(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE}/fichas/{self.ficha.pk}/estudiantes/{self.fe.pk}/',
            {
                'activo': False,
                'fecha_retiro': '2024-06-01',
                'motivo_retiro': FichaEstudiante.MotivoRetiro.DESERCION,
            },
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        self.fe.refresh_from_db()
        self.assertFalse(self.fe.activo)



class ReasignacionViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_reas@t.com')
        self.docente_user = make_user_docente(email='doc_reas@t.com')
        self.estudiante = make_estudiante(email='est_reas@t.com')
        self.ficha_origen = make_ficha()
        self.ficha_destino = make_ficha()
        self.fe = make_ficha_estudiante(
            ficha=self.ficha_origen, estudiante=self.estudiante, activo=True
        )

    def test_coord_crea_reasignacion(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/fichas/reasignaciones/create/', {
            'estudiante': self.estudiante.pk,
            'ficha_origen': self.ficha_origen.pk,
            'ficha_destino': self.ficha_destino.pk,
            'motivo': 'Cambio de jornada',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)
        self.fe.refresh_from_db()
        self.assertFalse(self.fe.activo)
        self.assertEqual(self.fe.motivo_retiro, FichaEstudiante.MotivoRetiro.REASIGNADO)

    def test_reasignacion_origen_igual_destino_invalida(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/fichas/reasignaciones/create/', {
            'estudiante': self.estudiante.pk,
            'ficha_origen': self.ficha_origen.pk,
            'ficha_destino': self.ficha_origen.pk,
            'motivo': 'Mismo',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_docente_no_puede_reasignar(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.post(f'{BASE}/fichas/reasignaciones/create/', {
            'estudiante': self.estudiante.pk,
            'ficha_origen': self.ficha_origen.pk,
            'ficha_destino': self.ficha_destino.pk,
            'motivo': 'Intento',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)


# ─────────────────────────────────────────────────────────────────────────────
# AULAS — Modelo
# ─────────────────────────────────────────────────────────────────────────────


