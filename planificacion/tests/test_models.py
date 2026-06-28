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

class PlanTrimestralModelTest(TestCase):

    def test_str_contiene_trimestre(self):
        plan = make_plan()
        self.assertIn('Trimestre', str(plan))

    def test_unique_together_ficha_trimestre(self):
        ficha = make_ficha()
        make_plan(ficha=ficha, trimestre=1)
        with self.assertRaises(Exception):
            PlanTrimestral.objects.create(
                ficha=ficha,
                trimestre=1,
                fecha_inicio=date(2024, 1, 1),
                fecha_fin=date(2024, 4, 30),
            )

    def test_fecha_fin_anterior_a_fecha_inicio_invalido(self):
        ficha = make_ficha()
        plan = PlanTrimestral(
            ficha=ficha, trimestre=2,
            fecha_inicio=date(2024, 6, 1),
            fecha_fin=date(2024, 1, 1),
        )
        with self.assertRaises(ValidationError):
            plan.clean()

    def test_total_horas_planificadas(self):
        plan = make_plan()
        make_item(plan=plan, horas=20)
        make_item(plan=plan, horas=15)
        self.assertEqual(plan.total_horas_planificadas, 35)

    def test_porcentaje_avance_sin_ejecucion_es_cero(self):
        plan = make_plan()
        make_item(plan=plan, horas=20)
        self.assertEqual(plan.porcentaje_avance, 0)

    def test_estado_inicial_es_borrador(self):
        plan = make_plan()
        self.assertEqual(plan.estado, PlanTrimestral.EstadoPlan.BORRADOR)



class ItemPlanModelTest(TestCase):

    def test_str_contiene_horas(self):
        item = make_item(horas=20)
        self.assertIn('20', str(item))

    def test_horas_cero_invalido(self):
        from planificacion.models.item_plan_model import ItemPlan
        plan = make_plan()
        comp = make_competencia()
        item = ItemPlan(plan=plan, competencia=comp, horas_asignadas=0, orden=1)
        with self.assertRaises(ValidationError):
            item.clean()

    def test_horas_negativas_invalido(self):
        from planificacion.models.item_plan_model import ItemPlan
        plan = make_plan()
        comp = make_competencia()
        item = ItemPlan(plan=plan, competencia=comp, horas_asignadas=-5, orden=1)
        with self.assertRaises(ValidationError):
            item.clean()

    def test_horas_restantes_sin_ejecucion_igual_asignadas(self):
        item = make_item(horas=20)
        self.assertEqual(item.horas_restantes, 20)

    def test_porcentaje_avance_sin_ejecucion_es_cero(self):
        item = make_item(horas=20)
        self.assertEqual(item.porcentaje_avance, 0)



class BloqueCompetenciaTest(TestCase):
    """
    Tests del modelo BloqueCompetencia — puente entre horario y currículo.
    Incluye el Bug #3 (horas_ejecutadas dinámico).
    """

    def setUp(self):
        self.docente = make_docente(email='bc@test.com')
        self.ficha = make_ficha()
        self.aula = make_aula()
        self.plan = make_plan(ficha=self.ficha)
        self.item = make_item(plan=self.plan, horas=20)

    def test_crear_bloque_competencia_con_horas_reales(self):
        """Bug #3 RESUELTO: horas_ejecutadas calculado desde duración real del slot."""
        from planificacion.models.bloque_competencia_model import BloqueCompetencia
        from decimal import Decimal

        bloque = make_bloque(
            docente=self.docente, ficha=self.ficha, aula=self.aula,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
        )
        # Duración real = 2 horas
        bc = BloqueCompetencia.objects.create(
            bloque=bloque, item_plan=self.item, horas_ejecutadas=Decimal('2.0'),
        )
        self.assertEqual(bc.horas_ejecutadas, Decimal('2.0'))

    def test_horas_ejecutadas_actualiza_item_horas_restantes(self):
        """horas_restantes de ItemPlan se calcula desde BloqueCompetencia.horas_ejecutadas."""
        from planificacion.models.bloque_competencia_model import BloqueCompetencia
        from decimal import Decimal

        bloque = make_bloque(
            docente=self.docente, ficha=self.ficha, aula=self.aula,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
        )
        BloqueCompetencia.objects.create(
            bloque=bloque, item_plan=self.item, horas_ejecutadas=Decimal('2.0'),
        )
        self.item.refresh_from_db()
        self.assertEqual(float(self.item.horas_restantes), 18.0)

    def test_one_to_one_bloque_no_puede_repetirse(self):
        from planificacion.models.bloque_competencia_model import BloqueCompetencia
        from decimal import Decimal

        bloque = make_bloque(
            docente=self.docente, ficha=self.ficha, aula=self.aula,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
        )
        BloqueCompetencia.objects.create(
            bloque=bloque, item_plan=self.item, horas_ejecutadas=Decimal('2.0'),
        )
        with self.assertRaises(IntegrityError):
            BloqueCompetencia.objects.create(
                bloque=bloque, item_plan=self.item, horas_ejecutadas=Decimal('2.0'),
            )


# ─────────────────────────────────────────────────────────────────────────────
# PlanTrimestral — Vistas
# ─────────────────────────────────────────────────────────────────────────────


