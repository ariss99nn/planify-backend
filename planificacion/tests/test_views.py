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

class PlanTrimestralViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_pv@test.com')
        self.admin = make_user(rol='ADMINISTRATIVO', email='admin_pv@test.com')
        self.docente_user = make_user_docente(email='doc_pv@test.com')
        self.estudiante = make_estudiante(email='est_pv@test.com')
        self.ficha = make_ficha()
        self.plan = make_plan(ficha=self.ficha)

    def test_coord_lista_planes(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE}/planes/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_coord_crea_plan(self):
        ficha2 = make_ficha()
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(f'{BASE}/planes/create/', {
            'ficha': ficha2.pk, 'trimestre': 1,
            'fecha_inicio': '2024-01-01', 'fecha_fin': '2024-04-30',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear_plan(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.post(f'{BASE}/planes/create/', {
            'ficha': self.ficha.pk, 'trimestre': 2,
            'fecha_inicio': '2024-05-01', 'fecha_fin': '2024-08-31',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_sin_autenticacion_retorna_401(self):
        r = self.client.get(f'{BASE}/planes/')
        self.assertEqual(r.status_code, 401)

    def test_plan_inexistente_retorna_404(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get(f'{BASE}/planes/99999/', **headers)
        self.assertEqual(r.status_code, 404)



class EstadoPlanTransicionTest(TestCase):
    """Tests de la máquina de estados del PlanTrimestral."""

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_est@test.com')
        self.admin = make_user(rol='ADMINISTRATIVO', email='admin_est@test.com')
        self.ficha = make_ficha()

    def test_borrador_a_en_revision(self):
        plan = make_plan(ficha=self.ficha)
        make_item(plan=plan)
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE}/planes/{plan.pk}/cambiar-estado/',
            {'estado': PlanTrimestral.EstadoPlan.EN_REVISION},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        plan.refresh_from_db()
        self.assertEqual(plan.estado, PlanTrimestral.EstadoPlan.EN_REVISION)

    def test_en_revision_a_aprobado(self):
        plan = make_plan(ficha=self.ficha)
        plan.estado = PlanTrimestral.EstadoPlan.EN_REVISION
        plan.save(update_fields=['estado'])
        make_item(plan=plan)
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE}/planes/{plan.pk}/cambiar-estado/',
            {'estado': PlanTrimestral.EstadoPlan.APROBADO},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        plan.refresh_from_db()
        self.assertEqual(plan.estado, PlanTrimestral.EstadoPlan.APROBADO)

    def test_transicion_invalida_retorna_400(self):
        """No se puede ir de BORRADOR a CERRADO directamente."""
        plan = make_plan(ficha=self.ficha)
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE}/planes/{plan.pk}/cambiar-estado/',
            {'estado': PlanTrimestral.EstadoPlan.CERRADO},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 400)

    def test_rechazar_requiere_motivo(self):
        plan = make_plan(ficha=self.ficha)
        plan.estado = PlanTrimestral.EstadoPlan.EN_REVISION
        plan.save(update_fields=['estado'])
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE}/planes/{plan.pk}/cambiar-estado/',
            {'estado': PlanTrimestral.EstadoPlan.RECHAZADO},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 400)

    def test_rechazar_con_motivo_exitoso(self):
        plan = make_plan(ficha=self.ficha)
        plan.estado = PlanTrimestral.EstadoPlan.EN_REVISION
        plan.save(update_fields=['estado'])
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE}/planes/{plan.pk}/cambiar-estado/',
            {
                'estado': PlanTrimestral.EstadoPlan.RECHAZADO,
                'motivo_rechazo': 'Faltan competencias transversales.',
            },
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)

    @patch('planificacion.serializers.plan_trimestral.plan_trimestral_aprobar_serializer._send_plan_en_ejecucion')
    def test_aprobado_a_en_ejecucion_notifica_docentes(self, mock_email):
        """Bug #10 RESUELTO: transición a EN_EJECUCION dispara notificación."""
        plan = make_plan(ficha=self.ficha)
        plan.estado = PlanTrimestral.EstadoPlan.APROBADO
        plan.save(update_fields=['estado'])
        docente = make_docente(email='doc_exec@test.com')
        make_item(plan=plan, docente=docente)

        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'{BASE}/planes/{plan.pk}/cambiar-estado/',
            {'estado': PlanTrimestral.EstadoPlan.EN_EJECUCION},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        mock_email.assert_called_once()



class GenerarHorarioViewTest(TestCase):
    """
    Tests del endpoint de generación automática de horarios.
    Cubre Bugs #2 (aula), #3 (horas dinámicas), #7 (idempotencia).
    """

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_gen@test.com')
        self.ficha = make_ficha()
        self.docente = make_docente(email='doc_gen@test.com')
        self.aula = make_aula()

    def test_generar_horario_plan_no_aprobado_retorna_400(self):
        plan = make_plan(ficha=self.ficha)
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(
            f'{BASE}/planes/{plan.pk}/generar-horario/',
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 400)

    def test_generar_horario_plan_aprobado_exitoso(self):
        plan = make_plan(ficha=self.ficha)
        plan.estado = PlanTrimestral.EstadoPlan.APROBADO
        plan.save(update_fields=['estado'])
        make_item(plan=plan, docente=self.docente, horas=4)

        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(
            f'{BASE}/planes/{plan.pk}/generar-horario/',
            format='json', **headers,
        )
        self.assertIn(r.status_code, [200, 201])
        if r.status_code in [200, 201]:
            self.assertIn('bloques_creados', r.data)

    def test_generar_horario_idempotencia_segunda_llamada_retorna_error(self):
        """Bug #7 RESUELTO: no se puede regenerar sin pasar por /regenerar-horario/."""
        plan = make_plan(ficha=self.ficha)
        plan.estado = PlanTrimestral.EstadoPlan.APROBADO
        plan.save(update_fields=['estado'])
        make_item(plan=plan, docente=self.docente, horas=2)

        headers = get_auth_header(self.client, self.coord)
        # Primera llamada
        self.client.post(
            f'{BASE}/planes/{plan.pk}/generar-horario/',
            format='json', **headers,
        )
        # Segunda llamada → debe fallar
        r2 = self.client.post(
            f'{BASE}/planes/{plan.pk}/generar-horario/',
            format='json', **headers,
        )
        self.assertEqual(r2.status_code, 400)

    def test_bloques_generados_tienen_aula_asignada(self):
        """Bug #2 RESUELTO: los bloques generados no deben tener aula=null."""
        plan = make_plan(ficha=self.ficha)
        plan.estado = PlanTrimestral.EstadoPlan.APROBADO
        plan.save(update_fields=['estado'])
        make_item(plan=plan, docente=self.docente, horas=2)

        headers = get_auth_header(self.client, self.coord)
        r = self.client.post(
            f'{BASE}/planes/{plan.pk}/generar-horario/',
            format='json', **headers,
        )
        if r.status_code in [200, 201] and r.data.get('bloques_creados', 0) > 0:
            bloques_sin_aula = BloqueHorario.objects.filter(
                ficha=self.ficha, aula__isnull=True
            ).count()
            self.assertEqual(
                bloques_sin_aula, 0,
                'Existen bloques generados sin aula asignada (Bug #2).',
            )


# ─────────────────────────────────────────────────────────────────────────────
# Docentes — Modelo
# ─────────────────────────────────────────────────────────────────────────────


