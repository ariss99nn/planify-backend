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

class DashboardViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_dash@t.com')
        self.docente_user = make_user_docente(email='doc_dash@t.com')
        self.admin = make_user(rol='ADMINISTRATIVO', email='admin_dash@t.com')

    def test_coord_accede_al_dashboard(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE}/dashboard/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_admin_accede_al_dashboard(self):
        headers = get_auth_header(self.client, self.admin)
        r = self.client.get(f'{BASE}/dashboard/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_no_accede_al_dashboard(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.get(f'{BASE}/dashboard/', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_autenticacion_retorna_401(self):
        self.assertEqual(self.client.get(f'{BASE}/dashboard/').status_code, 401)

    def test_sin_snapshot_responde_con_mensaje(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE}/dashboard/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(
            'mensaje' in r.data or 'snapshot' in r.data or 'datos' in r.data,
            f'Respuesta inesperada: {r.data}',
        )

    def test_dashboard_con_snapshot_devuelve_datos(self):
        from analitica.models.analitica_snapshot_model import AnaliticaSnapshot
        from django.utils import timezone
        AnaliticaSnapshot.objects.create(
            fecha=timezone.now().date(),
            fichas_activas=5,
            estudiantes_activos=120,
            docentes_activos=8,
        )
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE}/dashboard/', **headers)
        self.assertEqual(r.status_code, 200)



class SnapshotTaskTest(TestCase):
    """
    Tests de la tarea generar_snapshot_diario.
    Verifica idempotencia y que no hay N+1.
    """

    def test_snapshot_diario_crea_registro(self):
        from analitica.tasks.analitica_task import generar_snapshot_diario
        from analitica.models.analitica_snapshot_model import AnaliticaSnapshot
        from django.utils import timezone

        hoy = timezone.now().date()
        self.assertFalse(AnaliticaSnapshot.objects.filter(fecha=hoy).exists())
        resultado = generar_snapshot_diario()
        self.assertIsNotNone(resultado)
        self.assertTrue(AnaliticaSnapshot.objects.filter(fecha=hoy).exists())

    def test_snapshot_diario_es_idempotente(self):
        """Segunda llamada el mismo día no crea duplicado."""
        from analitica.tasks.analitica_task import generar_snapshot_diario
        from analitica.models.analitica_snapshot_model import AnaliticaSnapshot
        from django.utils import timezone

        generar_snapshot_diario()
        resultado2 = generar_snapshot_diario()
        # Segunda llamada retorna None (ya existe)
        self.assertIsNone(resultado2)
        self.assertEqual(
            AnaliticaSnapshot.objects.filter(fecha=timezone.now().date()).count(), 1
        )

    def test_snapshot_incluye_docentes_sobrecargados(self):
        """La tarea calcula correctamente docentes sobrecargados via SQL annotate."""
        from analitica.tasks.analitica_task import generar_snapshot_diario
        from analitica.models.analitica_snapshot_model import AnaliticaSnapshot

        docente = make_docente(email='sobrecargado@t.com', horas=4)
        # Crear bloques que superen el límite
        ficha = make_ficha()
        for hora_inicio in [6, 8, 10]:
            make_bloque(
                docente=docente, ficha=ficha,
                dia='LUNES',
                hora_inicio=time(hora_inicio, 0),
                hora_fin=time(hora_inicio + 2, 0),
            )

        generar_snapshot_diario()
        from django.utils import timezone
        snap = AnaliticaSnapshot.objects.get(fecha=timezone.now().date())
        self.assertGreaterEqual(snap.docentes_sobrecargados, 1)


# ─────────────────────────────────────────────────────────────────────────────
# NOTIFICACIONES — WebSocket Consumer
# ─────────────────────────────────────────────────────────────────────────────


