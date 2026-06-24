from django.test import TestCase
from competencia.tests.factories import (
    make_asignatura, make_competencia, make_rap,
    make_docente_asignatura,
)
from competencia.models.asignatura_model import Asignatura
from competencia.serializers import (
    AsignaturaCreateSerializer,
    AsignaturaUpdateSerializer,
    AsignaturaDetailSerializer,
    CompetenciaCreateSerializer,
    CompetenciaUpdateSerializer,
    CompetenciaDetailSerializer,
    RAPCreateSerializer,
    RAPUpdateSerializer,
    DocenteAsignaturaCreateSerializer,
)
from programa.tests.factories import make_modulo
from users.tests.factories import make_docente, make_user
from users.models.user import User


class AsignaturaSerializerTest(TestCase):

    def test_create_valido(self):
        modulo = make_modulo()
        data = {
            'modulo': modulo.pk,
            'nombre': 'Álgebra Lineal',
            'tipo': Asignatura.Tipo.TEORICA,
            'horas_lectivas': 80,
            'horas_practicas': 0,
            'orden': 1,
        }
        s = AsignaturaCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        a = s.save()
        self.assertEqual(a.nombre, 'Álgebra Lineal')

    def test_orden_duplicado_invalido(self):
        modulo = make_modulo()
        make_asignatura(modulo=modulo, orden=1)
        data = {
            'modulo': modulo.pk,
            'nombre': 'Otra',
            'tipo': Asignatura.Tipo.PRACTICA,
            'horas_lectivas': 40,
            'horas_practicas': 20,
            'orden': 1,
        }
        s = AsignaturaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('orden', s.errors)

    def test_horas_lectivas_cero_invalido(self):
        modulo = make_modulo()
        data = {
            'modulo': modulo.pk,
            'nombre': 'Test',
            'tipo': Asignatura.Tipo.TEORICA,
            'horas_lectivas': 0,
            'horas_practicas': 0,
            'orden': 10,
        }
        s = AsignaturaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('horas_lectivas', s.errors)

    def test_update_orden_mismo_invalido(self):
        modulo = make_modulo()
        make_asignatura(modulo=modulo, orden=1)
        a2 = make_asignatura(modulo=modulo, orden=2)
        s = AsignaturaUpdateSerializer(a2, data={'orden': 1}, partial=True)
        self.assertFalse(s.is_valid())
        self.assertIn('orden', s.errors)

    def test_update_mismo_orden_valido(self):
        a = make_asignatura(orden=1)
        s = AsignaturaUpdateSerializer(
            a, data={'orden': 1, 'nombre': 'Nuevo'}, partial=True
        )
        self.assertTrue(s.is_valid(), s.errors)

    def test_detail_anida_competencias(self):
        asignatura = make_asignatura()
        make_competencia(asignatura=asignatura)
        make_competencia(asignatura=asignatura)
        data = AsignaturaDetailSerializer(asignatura).data
        self.assertIn('competencias', data)
        self.assertEqual(len(data['competencias']), 2)

    def test_detail_anida_docentes_activos(self):
        asignatura = make_asignatura()
        docente = make_docente(email='doc_det@test.com')
        make_docente_asignatura(docente=docente, asignatura=asignatura, activo=True)
        docente2 = make_docente(email='doc_det2@test.com')
        make_docente_asignatura(docente=docente2, asignatura=asignatura, activo=False)
        data = AsignaturaDetailSerializer(asignatura).data
        self.assertEqual(len(data['docentes_asignados']), 1)


class CompetenciaSerializerTest(TestCase):

    def test_create_valido(self):
        asignatura = make_asignatura()
        data = {
            'asignatura': asignatura.pk,
            'codigo': 'comp-001',
            'nombre': 'Analizar sistemas',
        }
        s = CompetenciaCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        c = s.save()
        self.assertEqual(c.codigo, 'COMP-001')

    def test_codigo_normalizado_uppercase(self):
        asignatura = make_asignatura()
        data = {
            'asignatura': asignatura.pk,
            'codigo': 'comp-test',
            'nombre': 'Test',
        }
        s = CompetenciaCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        c = s.save()
        self.assertEqual(c.codigo, 'COMP-TEST')

    def test_codigo_duplicado_invalido(self):
        make_competencia(codigo='COMP-DUP')
        asignatura = make_asignatura()
        data = {
            'asignatura': asignatura.pk,
            'codigo': 'COMP-DUP',
            'nombre': 'Duplicada',
        }
        s = CompetenciaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('codigo', s.errors)

    def test_update_no_cambia_codigo(self):
        comp = make_competencia(codigo='COMP-ORIG')
        s = CompetenciaUpdateSerializer(
            comp, data={'nombre': 'Nombre nuevo'}, partial=True
        )
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        comp.refresh_from_db()
        self.assertEqual(comp.codigo, 'COMP-ORIG')

    def test_detail_anida_resultados(self):
        comp = make_competencia()
        make_rap(competencia=comp)
        make_rap(competencia=comp)
        data = CompetenciaDetailSerializer(comp).data
        self.assertIn('resultados', data)
        self.assertEqual(len(data['resultados']), 2)


class RAPSerializerTest(TestCase):

    def test_create_valido(self):
        comp = make_competencia()
        data = {
            'competencia': comp.pk,
            'codigo': 'rap-001',
            'descripcion': 'Aplica conceptos básicos.',
        }
        s = RAPCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        rap = s.save()
        self.assertEqual(rap.codigo, 'RAP-001')

    def test_codigo_normalizado_uppercase(self):
        comp = make_competencia()
        data = {
            'competencia': comp.pk,
            'codigo': 'rap-norm',
            'descripcion': 'Descripción.',
        }
        s = RAPCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        rap = s.save()
        self.assertEqual(rap.codigo, 'RAP-NORM')

    def test_codigo_duplicado_invalido(self):
        make_rap(codigo='RAP-DUP')
        comp = make_competencia()
        data = {
            'competencia': comp.pk,
            'codigo': 'RAP-DUP',
            'descripcion': 'Duplicado.',
        }
        s = RAPCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('codigo', s.errors)

    def test_update_solo_descripcion_y_criterios(self):
        rap = make_rap(descripcion='Original')
        s = RAPUpdateSerializer(
            rap,
            data={'descripcion': 'Actualizado', 'criterios_evaluacion': 'Nuevos criterios'},
            partial=True,
        )
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        rap.refresh_from_db()
        self.assertEqual(rap.descripcion, 'Actualizado')
        self.assertEqual(rap.criterios_evaluacion, 'Nuevos criterios')


class DocenteAsignaturaSerializerTest(TestCase):

    def test_create_valido(self):
        docente = make_docente(email='doc_da@test.com')
        asignatura = make_asignatura()
        data = {'docente': docente.pk, 'asignatura': asignatura.pk}
        s = DocenteAsignaturaCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        da = s.save()
        self.assertEqual(da.docente, docente)

    def test_rol_incorrecto_invalido(self):
        estudiante = make_user(rol=User.Rol.ESTUDIANTE, email='est_da@test.com')
        asignatura = make_asignatura()
        data = {'docente': estudiante.pk, 'asignatura': asignatura.pk}
        s = DocenteAsignaturaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('docente', s.errors)

    def test_asignacion_duplicada_invalida(self):
        docente = make_docente(email='doc_da2@test.com')
        asignatura = make_asignatura()
        make_docente_asignatura(docente=docente, asignatura=asignatura)
        data = {'docente': docente.pk, 'asignatura': asignatura.pk}
        s = DocenteAsignaturaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())

    def test_docente_inactivo_invalido(self):
        docente = make_docente(email='doc_da3@test.com', estado=False)
        asignatura = make_asignatura()
        data = {'docente': docente.pk, 'asignatura': asignatura.pk}
        s = DocenteAsignaturaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('docente', s.errors)