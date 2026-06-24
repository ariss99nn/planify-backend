from datetime import date
from django.test import TestCase
from .factories import make_plan, make_item
from planificacion.serializers import (
    PlanTrimestralCreateSerializer,
    PlanTrimestralAprobarSerializer,
    ItemPlanCreateSerializer,
    ItemPlanUpdateSerializer,
)
from ficha.tests.factories import make_ficha
from competencia.tests.factories import make_competencia
from users.tests.factories import make_coordinador


class PlanTrimestralSerializerTest(TestCase):

    def test_create_valido(self):
        ficha = make_ficha()
        data = {
            'ficha': ficha.pk,
            'trimestre': 1,
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-04-30',
        }
        s = PlanTrimestralCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        plan = s.save()
        self.assertEqual(plan.trimestre, 1)

    def test_trimestre_duplicado_invalido(self):
        ficha = make_ficha()
        make_plan(ficha=ficha, trimestre=1)
        data = {
            'ficha': ficha.pk,
            'trimestre': 1,
            'fecha_inicio': '2024-06-01',
            'fecha_fin': '2024-09-30',
        }
        s = PlanTrimestralCreateSerializer(data=data)
        self.assertFalse(s.is_valid())

    def test_aprobar_sin_items_invalido(self):
        plan = make_plan()
        s = PlanTrimestralAprobarSerializer(plan, data={'aprobado': True})
        self.assertFalse(s.is_valid())
        self.assertIn('aprobado', s.errors)

    def test_aprobar_con_items_valido(self):
        plan = make_plan()
        make_item(plan=plan)
        coord = make_coordinador(email='coord_plan@test.com')
        from rest_framework.test import APIRequestFactory
        request = APIRequestFactory().patch('/')
        request.user = coord
        s = PlanTrimestralAprobarSerializer(
            plan,
            data={'aprobado': True},
            context={'request': request},
        )
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        plan.refresh_from_db()
        self.assertTrue(plan.estado == plan.EstadoPlan.APROBADO)
        self.assertEqual(plan.aprobado_por, coord)


class ItemPlanSerializerTest(TestCase):

    def test_create_valido(self):
        plan = make_plan()
        comp = make_competencia()
        from docentes.tests.factories import make_docente
        from users.tests.factories import make_docente as make_docente_user
        docente_user = make_docente_user(email='doc_item_s@test.com')
        docente = make_docente(user=docente_user)
        data = {
            'plan': plan.pk,
            'competencia': comp.pk,
            'docente': docente.pk,
            'horas_asignadas': 20,
            'orden': 1,
        }
        s = ItemPlanCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        item = s.save()
        self.assertEqual(item.horas_asignadas, 20)

    def test_plan_aprobado_no_permite_crear(self):
        plan = make_plan(aprobado=True)
        comp = make_competencia()
        data = {
            'plan': plan.pk,
            'competencia': comp.pk,
            'horas_asignadas': 10,
            'orden': 1,
        }
        s = ItemPlanCreateSerializer(data=data)
        self.assertFalse(s.is_valid())

    def test_plan_aprobado_no_permite_editar(self):
        plan = make_plan(aprobado=True)
        item = make_item(plan=plan)
        s = ItemPlanUpdateSerializer(
            item, data={'horas_asignadas': 30}, partial=True
        )
        self.assertFalse(s.is_valid())