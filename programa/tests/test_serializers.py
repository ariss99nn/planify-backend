from datetime import date
from django.test import TestCase
from programa.tests.factories import make_programa, make_version, make_modulo
from programa.models.version_programa_model import VersionPrograma
from programa.models.modulo_model import Modulo
from programa.serializers import (
    ProgramaCreateSerializer,
    ProgramaUpdateSerializer,
    ProgramaDetailSerializer,
    VersionCreateSerializer,
    VersionUpdateSerializer,
    ModuloCreateSerializer,
    ModuloUpdateSerializer,
    DocenteModuloCreateSerializer,
)
from users.models.user import User
from users.tests.factories import make_docente, make_user


class ProgramaSerializerTest(TestCase):

    def test_create_valido(self):
        data = {
            'nombre': 'Administración',
            'nivel': Programa.Nivel.TECNOLOGIA,
            'horas_lectivas': 1800,
            'horas_practicas': 900,
        }
        from programa.models.programa_model import Programa
        s = ProgramaCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        p = s.save()
        self.assertEqual(p.nombre, 'Administración')

    def test_horas_lectivas_cero_invalido(self):
        data = {
            'nombre': 'Test',
            'nivel': Programa.Nivel.TECNICO,
            'horas_lectivas': 0,
            'horas_practicas': 100,
        }
        from programa.models.programa_model import Programa
        s = ProgramaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('horas_lectivas', s.errors)

    def test_horas_practicas_negativas_invalido(self):
        data = {
            'nombre': 'Test',
            'nivel': Programa.Nivel.TECNICO,
            'horas_lectivas': 100,
            'horas_practicas': -1,
        }
        from programa.models.programa_model import Programa
        s = ProgramaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())

    def test_detail_incluye_versiones(self):
        programa = make_programa()
        make_version(programa=programa, numero=1)
        make_version(programa=programa, numero=2)
        data = ProgramaDetailSerializer(programa).data
        self.assertIn('versiones', data)
        self.assertEqual(len(data['versiones']), 2)

    def test_update_parcial(self):
        programa = make_programa(nombre='Original')
        s = ProgramaUpdateSerializer(
            programa, data={'nombre': 'Actualizado'}, partial=True
        )
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        programa.refresh_from_db()
        self.assertEqual(programa.nombre, 'Actualizado')


class VersionSerializerTest(TestCase):

    def test_create_valido(self):
        programa = make_programa()
        data = {
            'programa': programa.pk,
            'numero': 1,
            'vigente': True,
            'fecha_inicio': '2024-01-01',
        }
        s = VersionCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        v = s.save()
        self.assertEqual(v.numero, 1)

    def test_numero_duplicado_en_programa(self):
        programa = make_programa()
        make_version(programa=programa, numero=1)
        data = {
            'programa': programa.pk,
            'numero': 1,
            'vigente': False,
            'fecha_inicio': '2024-06-01',
        }
        s = VersionCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('numero', s.errors)

    def test_fecha_fin_anterior_a_inicio_invalida(self):
        programa = make_programa()
        data = {
            'programa': programa.pk,
            'numero': 5,
            'vigente': False,
            'fecha_inicio': '2024-06-01',
            'fecha_fin': '2024-01-01',
        }
        s = VersionCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('fecha_fin', s.errors)

    def test_update_no_cambia_programa(self):
        version = make_version()
        otro_programa = make_programa()
        s = VersionUpdateSerializer(
            version,
            data={'descripcion': 'Nueva descripción'},
            partial=True,
        )
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        version.refresh_from_db()
        self.assertNotEqual(version.programa, otro_programa)


class ModuloSerializerTest(TestCase):

    def test_create_valido(self):
        version = make_version()
        data = {
            'version': version.pk,
            'nombre': 'Redes',
            'orden': 1,
            'horas_lectivas': 60,
            'horas_practicas': 30,
        }
        s = ModuloCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        m = s.save()
        self.assertEqual(m.nombre, 'Redes')

    def test_orden_duplicado_en_version(self):
        version = make_version()
        make_modulo(version=version, orden=1)
        data = {
            'version': version.pk,
            'nombre': 'Otro',
            'orden': 1,
            'horas_lectivas': 40,
            'horas_practicas': 20,
        }
        s = ModuloCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('orden', s.errors)

    def test_horas_lectivas_cero_invalido(self):
        version = make_version()
        data = {
            'version': version.pk,
            'nombre': 'Test',
            'orden': 10,
            'horas_lectivas': 0,
            'horas_practicas': 20,
        }
        s = ModuloCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('horas_lectivas', s.errors)

    def test_update_orden_duplicado_invalido(self):
        version = make_version()
        make_modulo(version=version, orden=1)
        modulo2 = make_modulo(version=version, orden=2)
        s = ModuloUpdateSerializer(
            modulo2, data={'orden': 1}, partial=True
        )
        self.assertFalse(s.is_valid())
        self.assertIn('orden', s.errors)

    def test_update_mismo_orden_valido(self):
        modulo = make_modulo(orden=1)
        s = ModuloUpdateSerializer(
            modulo, data={'orden': 1, 'nombre': 'Nuevo nombre'}, partial=True
        )
        self.assertTrue(s.is_valid(), s.errors)


class DocenteModuloSerializerTest(TestCase):

    def test_create_valido(self):
        docente = make_docente(email='doc_serial@test.com')
        modulo = make_modulo()
        data = {'docente': docente.pk, 'modulo': modulo.pk}
        s = DocenteModuloCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        dm = s.save()
        self.assertEqual(dm.docente, docente)

    def test_rol_incorrecto_invalido(self):
        estudiante = make_user(rol=User.Rol.ESTUDIANTE, email='est_serial@test.com')
        modulo = make_modulo()
        data = {'docente': estudiante.pk, 'modulo': modulo.pk}
        s = DocenteModuloCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('docente', s.errors)

    def test_asignacion_duplicada_invalida(self):
        from programa.tests.factories import make_docente_modulo
        docente = make_docente(email='doc_dup@test.com')
        modulo = make_modulo()
        make_docente_modulo(docente=docente, modulo=modulo)
        data = {'docente': docente.pk, 'modulo': modulo.pk}
        s = DocenteModuloCreateSerializer(data=data)
        self.assertFalse(s.is_valid())

    def test_docente_inactivo_invalido(self):
        docente = make_docente(email='doc_inact@test.com', estado=False)
        modulo = make_modulo()
        data = {'docente': docente.pk, 'modulo': modulo.pk}
        s = DocenteModuloCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('docente', s.errors)