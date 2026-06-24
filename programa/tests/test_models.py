from django.test import TestCase
from datetime import date
from programa.tests.factories import make_programa, make_version, make_modulo
from programa.models.programa_model import Programa
from programa.models.version_programa_model import VersionPrograma
from programa.models.modulo_model import Modulo


class ProgramaModelTest(TestCase):

    def test_str(self):
        p = make_programa(nombre='Gestión Empresarial', nivel=Programa.Nivel.TECNOLOGIA)
        self.assertIn('Gestión Empresarial', str(p))
        self.assertIn('Tecnología', str(p))

    def test_total_horas_property(self):
        p = make_programa(horas_lectivas=1000, horas_practicas=500)
        self.assertEqual(p.total_horas, 1500)

    def test_estado_default_activo(self):
        p = make_programa()
        self.assertEqual(p.estado, Programa.Estado.ACTIVO)

    def test_ordering_por_nombre(self):
        make_programa(nombre='Z Programa')
        make_programa(nombre='A Programa')
        nombres = list(Programa.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, sorted(nombres))

    def test_updated_at_se_actualiza(self):
        p = make_programa()
        original = p.updated_at
        p.nombre = 'Nombre Cambiado'
        p.save(update_fields=['nombre'])
        p.refresh_from_db()
        self.assertGreaterEqual(p.updated_at, original)


class VersionProgramaModelTest(TestCase):

    def test_str(self):
        v = make_version(numero=2)
        self.assertIn('v2', str(v))

    def test_solo_una_version_vigente_por_programa(self):
        programa = make_programa()
        v1 = make_version(programa=programa, numero=1, vigente=True)
        v2 = make_version(programa=programa, numero=2, vigente=True)
        v1.refresh_from_db()
        self.assertFalse(v1.vigente)
        self.assertTrue(v2.vigente)

    def test_unique_together_programa_numero(self):
        programa = make_programa()
        make_version(programa=programa, numero=1)
        with self.assertRaises(Exception):
            VersionPrograma.objects.create(
                programa=programa,
                numero=1,
                vigente=False,
                fecha_inicio=date(2024, 6, 1),
            )

    def test_version_no_vigente_no_afecta_otras(self):
        programa = make_programa()
        v1 = make_version(programa=programa, numero=1, vigente=True)
        v2 = make_version(programa=programa, numero=2, vigente=False)
        v1.refresh_from_db()
        self.assertTrue(v1.vigente)
        self.assertFalse(v2.vigente)


class ModuloModelTest(TestCase):

    def test_str(self):
        modulo = make_modulo(nombre='Bases de Datos')
        self.assertIn('Bases de Datos', str(modulo))

    def test_total_horas_property(self):
        modulo = make_modulo(horas_lectivas=60, horas_practicas=30)
        self.assertEqual(modulo.total_horas, 90)

    def test_unique_together_version_orden(self):
        version = make_version()
        make_modulo(version=version, orden=1)
        with self.assertRaises(Exception):
            Modulo.objects.create(
                version=version,
                nombre='Otro módulo',
                orden=1,
                horas_lectivas=40,
                horas_practicas=20,
            )

    def test_ordering_por_version_y_orden(self):
        version = make_version()
        make_modulo(version=version, nombre='Módulo B', orden=2)
        make_modulo(version=version, nombre='Módulo A', orden=1)
        ordenes = list(
            Modulo.objects.filter(version=version).values_list('orden', flat=True)
        )
        self.assertEqual(ordenes, sorted(ordenes))

    def test_estado_default_activo(self):
        modulo = make_modulo()
        self.assertEqual(modulo.estado, Modulo.Estado.ACTIVO)

    def test_proteccion_al_eliminar_version(self):
        from django.db.models.deletion import ProtectedError
        version = make_version()
        make_modulo(version=version)
        with self.assertRaises(ProtectedError):
            version.delete()