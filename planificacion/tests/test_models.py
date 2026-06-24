from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from .factories import make_plan, make_item
from planificacion.models.plan_trimestral_model import PlanTrimestral
from ficha.tests.factories import make_ficha
from competencia.tests.factories import make_competencia


class PlanTrimestralModelTest(TestCase):

    def test_str(self):
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

    def test_fecha_fin_anterior_invalida(self):
        ficha = make_ficha()
        plan = PlanTrimestral(
            ficha=ficha,
            trimestre=2,
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

    def test_porcentaje_avance_sin_ejecucion(self):
        plan = make_plan()
        make_item(plan=plan, horas=20)
        self.assertEqual(plan.porcentaje_avance, 0)


class ItemPlanModelTest(TestCase):

    def test_str(self):
        item = make_item(horas=20)
        self.assertIn('20h', str(item))

    def test_horas_cero_invalido(self):
        from planificacion.models.item_plan_model import ItemPlan
        plan = make_plan()
        comp = make_competencia()
        item = ItemPlan(plan=plan, competencia=comp, horas_asignadas=0, orden=1)
        with self.assertRaises(ValidationError):
            item.clean()

    def test_horas_restantes_sin_ejecucion(self):
        item = make_item(horas=20)
        self.assertEqual(item.horas_restantes, 20)

    def test_porcentaje_avance(self):
        item = make_item(horas=20)
        self.assertEqual(item.porcentaje_avance, 0)