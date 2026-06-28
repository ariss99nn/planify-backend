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

class ReporteFactoryTest(TestCase):
    """
    Verifica que TODOS los tipos declarados en el modelo tengan
    un generador registrado. CORRECCIÓN: en la versión original
    faltaban HORARIOS, COMPETENCIAS, PLANES.
    """

    def test_todos_los_tipos_tienen_generador(self):
        from reportes.services.reporte_factory import ReporteFactory
        from reportes.models.reporte_generado_model import ReporteGenerado

        tipos_declarados = [
            choice[0] for choice in ReporteGenerado.TipoReporte.choices
        ]
        for tipo in tipos_declarados:
            try:
                generador = ReporteFactory.obtener(tipo)
                self.assertIsNotNone(generador, f'Tipo {tipo} sin generador.')
            except (KeyError, ValueError) as e:
                self.fail(
                    f'TipoReporte.{tipo} no tiene generador registrado en '
                    f'ReporteFactory: {e}'
                )

    def test_tipo_invalido_lanza_excepcion(self):
        from reportes.services.reporte_factory import ReporteFactory
        with self.assertRaises((KeyError, ValueError)):
            ReporteFactory.obtener('TIPO_QUE_NO_EXISTE')

    def test_generador_fichas_crea_headers_y_rows(self):
        from reportes.services.generators.ficha_generator import FichaReportGenerator
        make_ficha()
        gen = FichaReportGenerator(filtros={})
        headers = gen._get_headers()
        qs = gen._get_queryset()
        self.assertIsInstance(headers, list)
        self.assertGreater(len(headers), 0)

    def test_generador_horarios_crea_headers(self):
        """NUEVO: generador de horarios implementado correctamente."""
        from reportes.services.generators.horario_generator import HorarioReportGenerator
        gen = HorarioReportGenerator(filtros={})
        headers = gen._get_headers()
        self.assertIn('Día', headers)
        self.assertIn('Docente', headers)
        self.assertIn('Aula', headers)

    def test_generador_competencias_crea_headers(self):
        """NUEVO: generador de competencias implementado correctamente."""
        from reportes.services.generators.competencia_generator import CompetenciaReportGenerator
        gen = CompetenciaReportGenerator(filtros={})
        headers = gen._get_headers()
        self.assertIn('Competencia', headers)
        self.assertIn('Programa', headers)

    def test_generador_planes_crea_headers(self):
        """NUEVO: generador de planes implementado correctamente."""
        from reportes.services.generators.plan_generator import PlanReportGenerator
        gen = PlanReportGenerator(filtros={})
        headers = gen._get_headers()
        self.assertIn('Estado', headers)
        self.assertIn('Ficha', headers)



class ReporteSolicitarViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_rep@t.com')
        self.docente_user = make_user_docente(email='doc_rep@t.com')

    def test_solicitar_reporte_fichas(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/reportes/solicitar/', {
            'tipo': 'FICHAS', 'filtros': {},
        }, format='json', **headers)
        self.assertIn(r.status_code, [200, 201, 202])

    def test_solicitar_reporte_horarios(self):
        """NUEVO: tipo HORARIOS ahora tiene generador."""
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/reportes/solicitar/', {
            'tipo': 'HORARIOS', 'filtros': {},
        }, format='json', **headers)
        self.assertIn(r.status_code, [200, 201, 202])

    def test_tipo_invalido_retorna_400(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/reportes/solicitar/', {
            'tipo': 'INVALIDO', 'filtros': {},
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_docente_no_puede_solicitar(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.post(f'{BASE}/reportes/solicitar/', {
            'tipo': 'FICHAS',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_autenticacion_retorna_401(self):
        r = self.client.post(f'{BASE}/reportes/solicitar/', {
            'tipo': 'FICHAS',
        }, format='json')
        self.assertEqual(r.status_code, 401)

    def test_reporte_inexistente_retorna_404(self):
        headers = get_auth_header(self.client, self.coord)
        self.assertEqual(
            self.client.get(f'{BASE}/reportes/99999/', **headers).status_code, 404
        )


# ─────────────────────────────────────────────────────────────────────────────
# ANALÍTICA — Dashboard y Snapshot Task
# ─────────────────────────────────────────────────────────────────────────────


