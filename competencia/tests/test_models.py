# competencia/tests/test_models.py
"""
Tests del módulo competencia: Asignatura, Competencia, ResultadoAprendizaje.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

from competencia.models.asignatura_model import Asignatura
from competencia.models.competencia_model import Competencia
from competencia.models.resultado_aprendizaje_model import ResultadoAprendizaje
from competencia.tests.factories import (
    make_asignatura, make_competencia, make_competencia_transversal, make_rap,
)
from programa.tests.factories import make_modulo


class AsignaturaModelTest(TestCase):

    def test_str_contiene_nombre_modulo_y_nombre(self):
        m = make_modulo(nombre='Redes')
        a = make_asignatura(modulo=m, nombre='TCP/IP')
        self.assertIn('TCP/IP', str(a))

    def test_total_horas(self):
        a = make_asignatura(horas_lectivas=60, horas_practicas=30)
        self.assertEqual(a.total_horas, 90)

    def test_estado_default_activa(self):
        self.assertEqual(make_asignatura().estado, Asignatura.Estado.ACTIVA)

    def test_horas_lectivas_cero_invalido(self):
        with self.assertRaises(ValidationError) as ctx:
            Asignatura.objects.create(
                modulo=make_modulo(), nombre='Test', tipo=Asignatura.Tipo.TEORICA,
                horas_lectivas=0, horas_practicas=0, orden=99,
            )
        self.assertIn('horas_lectivas', ctx.exception.message_dict)

    def test_horas_practicas_negativas_invalido(self):
        with self.assertRaises(ValidationError) as ctx:
            Asignatura.objects.create(
                modulo=make_modulo(), nombre='Test', tipo=Asignatura.Tipo.PRACTICA,
                horas_lectivas=40, horas_practicas=-5, orden=99,
            )
        self.assertIn('horas_practicas', ctx.exception.message_dict)

    def test_unique_together_modulo_orden(self):
        modulo = make_modulo()
        make_asignatura(modulo=modulo, orden=1)
        with self.assertRaises(Exception):
            Asignatura.objects.create(
                modulo=modulo, nombre='Duplicada', tipo=Asignatura.Tipo.TEORICA,
                horas_lectivas=40, horas_practicas=0, orden=1,
            )

    def test_ordering_por_modulo_y_orden(self):
        modulo = make_modulo()
        make_asignatura(modulo=modulo, orden=3)
        make_asignatura(modulo=modulo, orden=1)
        make_asignatura(modulo=modulo, orden=2)
        ordenes = list(
            Asignatura.objects.filter(modulo=modulo).values_list('orden', flat=True)
        )
        self.assertEqual(ordenes, sorted(ordenes))

    def test_modulo_protegido_al_eliminar(self):
        modulo = make_modulo()
        make_asignatura(modulo=modulo)
        with self.assertRaises(ProtectedError):
            modulo.delete()


class CompetenciaModelTest(TestCase):

    def test_str_contiene_tipo_codigo_y_nombre(self):
        comp = make_competencia(codigo='TEST-001', nombre='Resolver Problemas')
        s = str(comp)
        self.assertIn('TEST-001', s)
        self.assertIn('Resolver Problemas', s)

    def test_competencia_principal_requiere_asignatura(self):
        with self.assertRaises(ValidationError) as ctx:
            Competencia.objects.create(
                asignatura=None,
                tipo=Competencia.TipoCompetencia.PRINCIPAL,
                codigo='NOASIG-001',
                nombre='Sin asignatura',
            )
        self.assertIn('asignatura', ctx.exception.message_dict)

    def test_competencia_transversal_no_puede_tener_asignatura(self):
        asignatura = make_asignatura()
        with self.assertRaises(ValidationError) as ctx:
            Competencia.objects.create(
                asignatura=asignatura,
                tipo=Competencia.TipoCompetencia.TRANSVERSAL,
                codigo='TRANS-CON-ASIG',
                nombre='Transversal con asignatura',
                horas_trimestre_transversal=4,
            )
        self.assertIn('asignatura', ctx.exception.message_dict)

    def test_competencia_transversal_requiere_horas(self):
        with self.assertRaises(ValidationError) as ctx:
            Competencia.objects.create(
                asignatura=None,
                tipo=Competencia.TipoCompetencia.TRANSVERSAL,
                codigo='TRANS-SIN-HORAS',
                nombre='Sin horas',
                horas_trimestre_transversal=None,  # obligatorio
            )
        self.assertIn('horas_trimestre_transversal', ctx.exception.message_dict)

    def test_codigo_unico(self):
        make_competencia(codigo='UNICO-001')
        with self.assertRaises(Exception):
            Competencia.objects.create(
                asignatura=make_asignatura(),
                tipo=Competencia.TipoCompetencia.PRINCIPAL,
                codigo='UNICO-001',
                nombre='Duplicada',
            )

    def test_ordering_por_tipo_y_codigo(self):
        make_competencia(codigo='B-COMP')
        make_competencia(codigo='A-COMP')
        codigos = list(Competencia.objects.values_list('codigo', flat=True))
        self.assertEqual(codigos, sorted(codigos))

    def test_competencia_transversal_valida(self):
        trans = make_competencia_transversal(horas_trimestre_transversal=4)
        self.assertIsNone(trans.asignatura)
        self.assertEqual(trans.tipo, Competencia.TipoCompetencia.TRANSVERSAL)
        self.assertEqual(trans.horas_trimestre_transversal, 4)

    def test_principal_no_puede_tener_horas_trimestre_transversal(self):
        with self.assertRaises(ValidationError) as ctx:
            Competencia.objects.create(
                asignatura=make_asignatura(),
                tipo=Competencia.TipoCompetencia.PRINCIPAL,
                codigo='PRIN-HORAS',
                nombre='Principal con horas transversal',
                horas_trimestre_transversal=4,  # inválido para PRINCIPAL
            )
        self.assertIn('horas_trimestre_transversal', ctx.exception.message_dict)

    def test_es_induccion_solo_en_transversales(self):
        with self.assertRaises(ValidationError) as ctx:
            Competencia.objects.create(
                asignatura=make_asignatura(),
                tipo=Competencia.TipoCompetencia.PRINCIPAL,
                codigo='INDUCCION-PRINCIPAL',
                nombre='Inducción principal inválida',
                es_induccion=True,
            )
        self.assertIn('es_induccion', ctx.exception.message_dict)

    def test_competencia_protegida_por_rap(self):
        comp = make_competencia()
        make_rap(competencia=comp)
        with self.assertRaises(ProtectedError):
            comp.delete()


class ResultadoAprendizajeModelTest(TestCase):

    def test_str_contiene_codigo_y_descripcion_truncada(self):
        rap = make_rap(codigo='RAP-STR', descripcion='A' * 80)
        s = str(rap)
        self.assertIn('RAP-STR', s)
        # descripcion se trunca a 60 chars
        self.assertLessEqual(len(s), 100)

    def test_codigo_unico(self):
        make_rap(codigo='RAP-UNICO')
        with self.assertRaises(Exception):
            ResultadoAprendizaje.objects.create(
                competencia=make_competencia(),
                codigo='RAP-UNICO',
                descripcion='Duplicado.',
            )

    def test_ordering_por_competencia_y_codigo(self):
        comp = make_competencia()
        make_rap(competencia=comp, codigo='Z-RAP')
        make_rap(competencia=comp, codigo='A-RAP')
        codigos = list(
            ResultadoAprendizaje.objects.filter(competencia=comp)
            .values_list('codigo', flat=True)
        )
        self.assertEqual(codigos, sorted(codigos))