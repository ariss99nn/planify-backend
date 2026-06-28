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

class ExportacionServiceTest(TestCase):
    """
    Tests unitarios del ExportacionService.
    Verifica que TODOS los módulos retornen headers y rows correctos.
    CORRECCIÓN: se agregan los módulos faltantes (ESTUDIANTES, AULAS,
    PLANES, COMPETENCIAS) que no tenían tests en la versión original.
    """

    def test_exportar_fichas_retorna_headers_y_rows(self):
        from exportacion.services.exportacion_service import ExportacionService
        make_ficha()
        headers, rows = ExportacionService.exportar_fichas({})
        self.assertIsInstance(headers, list)
        self.assertGreater(len(headers), 0)
        self.assertIsInstance(rows, list)

    def test_exportar_docentes_retorna_headers_y_rows(self):
        from exportacion.services.exportacion_service import ExportacionService
        make_docente(email='exp_doc@t.com')
        headers, rows = ExportacionService.exportar_docentes({})
        self.assertIsInstance(headers, list)
        self.assertGreater(len(headers), 0)

    def test_exportar_horarios_retorna_headers_y_rows(self):
        from exportacion.services.exportacion_service import ExportacionService
        headers, rows = ExportacionService.exportar_horarios({})
        self.assertIsInstance(headers, list)
        self.assertGreater(len(headers), 0)

    def test_exportar_estudiantes_retorna_headers_y_rows(self):
        """NUEVO: módulo ESTUDIANTES — antes faltaba implementación y test."""
        from exportacion.services.exportacion_service import ExportacionService
        est = make_estudiante(email='exp_est@t.com')
        ficha = make_ficha()
        make_ficha_estudiante(ficha=ficha, estudiante=est, activo=True)
        headers, rows = ExportacionService.exportar_estudiantes({})
        self.assertIsInstance(headers, list)
        self.assertGreater(len(headers), 0)

    def test_exportar_aulas_retorna_headers_y_rows(self):
        """NUEVO: módulo AULAS — antes faltaba implementación y test."""
        from exportacion.services.exportacion_service import ExportacionService
        make_aula()
        headers, rows = ExportacionService.exportar_aulas({})
        self.assertIsInstance(headers, list)
        self.assertGreater(len(headers), 0)

    def test_exportar_planes_retorna_headers_y_rows(self):
        """NUEVO: módulo PLANES — antes faltaba implementación y test."""
        from exportacion.services.exportacion_service import ExportacionService
        from planificacion.tests.factories import make_plan
        make_plan()
        headers, rows = ExportacionService.exportar_planes({})
        self.assertIsInstance(headers, list)
        self.assertGreater(len(headers), 0)

    def test_exportar_competencias_retorna_headers_y_rows(self):
        """NUEVO: módulo COMPETENCIAS — antes faltaba implementación y test."""
        from exportacion.services.exportacion_service import ExportacionService
        make_competencia()
        headers, rows = ExportacionService.exportar_competencias({})
        self.assertIsInstance(headers, list)
        self.assertGreater(len(headers), 0)

    def test_modulo_invalido_lanza_value_error(self):
        from exportacion.services.exportacion_service import ExportacionService
        with self.assertRaises(ValueError):
            ExportacionService.exportar('INVALIDO', {})

    def test_a_csv_retorna_bytes_validos(self):
        from exportacion.services.exportacion_service import ExportacionService
        headers = ['col1', 'col2']
        rows = [['val1', 'val2'], ['=formula', 'safe']]
        csv_bytes = ExportacionService.a_csv(headers, rows)
        self.assertIsInstance(csv_bytes, bytes)
        contenido = csv_bytes.decode('utf-8-sig')
        self.assertIn('col1', contenido)
        # CSV injection: =formula debe ser escapado como '=formula
        self.assertNotIn('=formula', contenido)
        self.assertIn("'=formula", contenido)

    def test_a_excel_retorna_bytes_validos(self):
        from exportacion.services.exportacion_service import ExportacionService
        headers = ['col1', 'col2']
        rows = [['val1', 'val2']]
        excel_bytes = ExportacionService.a_excel(headers, rows)
        self.assertIsInstance(excel_bytes, bytes)
        self.assertGreater(len(excel_bytes), 0)

    def test_prevencion_csv_injection(self):
        """Valores que empiezan con =, +, -, @ deben ser escapados."""
        from exportacion.services.exportacion_service import ExportacionService
        peligrosos = ['=cmd', '+cmd', '-cmd', '@cmd']
        for val in peligrosos:
            sanitizado = ExportacionService._prevenir_formula(val)
            self.assertTrue(
                sanitizado.startswith("'"),
                f"No se escapó el valor peligroso: {val}",
            )



class ExportacionViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_exp@t.com')
        self.docente_user = make_user_docente(email='doc_exp@t.com')

    def test_exportar_fichas_csv(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/exportar/', {
            'modulo': 'FICHAS', 'formato': 'csv', 'filtros': {},
        }, format='json', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('text/csv', r['Content-Type'])

    def test_exportar_docentes_excel(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/exportar/', {
            'modulo': 'DOCENTES', 'formato': 'excel',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn('spreadsheetml', r['Content-Type'])

    def test_exportar_horarios_csv(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/exportar/', {
            'modulo': 'HORARIOS', 'formato': 'csv',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 200)

    def test_exportar_estudiantes_csv(self):
        """NUEVO: endpoint ESTUDIANTES correctamente implementado."""
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/exportar/', {
            'modulo': 'ESTUDIANTES', 'formato': 'csv',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 200)

    def test_exportar_aulas_csv(self):
        """NUEVO: endpoint AULAS correctamente implementado."""
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/exportar/', {
            'modulo': 'AULAS', 'formato': 'csv',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 200)

    def test_exportar_planes_csv(self):
        """NUEVO: endpoint PLANES correctamente implementado."""
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/exportar/', {
            'modulo': 'PLANES', 'formato': 'csv',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 200)

    def test_exportar_competencias_csv(self):
        """NUEVO: endpoint COMPETENCIAS correctamente implementado."""
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/exportar/', {
            'modulo': 'COMPETENCIAS', 'formato': 'csv',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 200)

    def test_modulo_invalido_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/exportar/', {
            'modulo': 'INVALIDO', 'formato': 'csv',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_docente_no_puede_exportar(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.post(f'{BASE}/exportar/', {
            'modulo': 'FICHAS', 'formato': 'csv',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_autenticacion_retorna_401(self):
        r = self.client.post(f'{BASE}/exportar/', {
            'modulo': 'FICHAS', 'formato': 'csv',
        }, format='json')
        self.assertEqual(r.status_code, 401)


# ─────────────────────────────────────────────────────────────────────────────
# REPORTES — Factory y Vistas
# ─────────────────────────────────────────────────────────────────────────────


