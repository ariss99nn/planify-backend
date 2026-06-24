from django.test import TestCase
from competencia.tests.factories import (
    make_asignatura, make_competencia, make_rap,
)
from competencia.models.asignatura_model import Asignatura
from competencia.models.competencia_model import Competencia
from competencia.models.resultado_aprendizaje_model import ResultadoAprendizaje
from programa.tests.factories import make_modulo


class AsignaturaModelTest(TestCase):

    def test_str(self):
        asignatura = make_asignatura(nombre='Redes de Computadores')
        self.assertIn('Redes de Computadores', str(asignatura))

    def test_total_horas_property(self):
        asignatura = make_asignatura(horas_lectivas=60, horas_practicas=30)
        self.assertEqual(asignatura.total_horas, 90)

    def test_estado_default_activa(self):
        asignatura = make_asignatura()
        self.assertEqual(asignatura.estado, Asignatura.Estado.ACTIVA)

    def test_unique_together_modulo_orden(self):
        modulo = make_modulo()
        make_asignatura(modulo=modulo, orden=1)
        with self.assertRaises(Exception):
            Asignatura.objects.create(
                modulo=modulo,
                nombre='Otra asignatura',
                tipo=Asignatura.Tipo.TEORICA,
                horas_lectivas=40,
                horas_practicas=0,
                orden=1,
            )

    def test_ordering_por_modulo_y_orden(self):
        modulo = make_modulo()
        make_asignatura(modulo=modulo, nombre='Z Asig', orden=3)
        make_asignatura(modulo=modulo, nombre='A Asig', orden=1)
        ordenes = list(
            Asignatura.objects.filter(modulo=modulo).values_list('orden', flat=True)
        )
        self.assertEqual(ordenes, sorted(ordenes))

    def test_proteccion_al_eliminar_modulo(self):
        from django.db.models.deletion import ProtectedError
        modulo = make_modulo()
        make_asignatura(modulo=modulo)
        with self.assertRaises(ProtectedError):
            modulo.delete()


class CompetenciaModelTest(TestCase):

    def test_str(self):
        comp = make_competencia(codigo='COMP-TEST', nombre='Resolver problemas')
        self.assertIn('COMP-TEST', str(comp))
        self.assertIn('Resolver problemas', str(comp))

    def test_codigo_unico(self):
        make_competencia(codigo='COMP-UNICO')
        with self.assertRaises(Exception):
            asignatura = make_asignatura()
            Competencia.objects.create(
                asignatura=asignatura,
                codigo='COMP-UNICO',
                nombre='Duplicada',
            )

    def test_ordering_por_asignatura_y_codigo(self):
        asignatura = make_asignatura()
        make_competencia(asignatura=asignatura, codigo='COMP-Z')
        make_competencia(asignatura=asignatura, codigo='COMP-A')
        codigos = list(
            Competencia.objects.filter(
                asignatura=asignatura
            ).values_list('codigo', flat=True)
        )
        self.assertEqual(codigos, sorted(codigos))


class ResultadoAprendizajeModelTest(TestCase):

    def test_str_trunca_descripcion(self):
        rap = make_rap(
            descripcion='A' * 80
        )
        self.assertLessEqual(len(str(rap)), 80)

    def test_codigo_unico(self):
        make_rap(codigo='RAP-UNICO')
        with self.assertRaises(Exception):
            comp = make_competencia()
            ResultadoAprendizaje.objects.create(
                competencia=comp,
                codigo='RAP-UNICO',
                descripcion='Duplicado',
            )

    def test_proteccion_al_eliminar_competencia(self):
        from django.db.models.deletion import ProtectedError
        comp = make_competencia()
        make_rap(competencia=comp)
        with self.assertRaises(ProtectedError):
            comp.delete()