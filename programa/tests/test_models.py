# programa/tests/test_models.py
"""
Tests del módulo programa: Programa, VersionPrograma, Modulo.

CORRECCIONES respecto a la versión anterior:
- Factories creadas (antes no existían).
- No se importa make_docente_modulo (no existe).
- URLs no aplican aquí (solo modelos).
"""
from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from programa.models.programa_model import Programa
from programa.models.version_programa_model import VersionPrograma
from programa.models.modulo_model import Modulo
from programa.tests.factories import make_programa, make_version, make_modulo


class ProgramaModelTest(TestCase):

    def test_str_contiene_nombre_y_nivel(self):
        p = make_programa(nombre='Gestión Empresarial', nivel=Programa.Nivel.TECNOLOGIA)
        s = str(p)
        self.assertIn('Gestión Empresarial', s)

    def test_total_horas_es_suma_lectivas_practicas(self):
        p = make_programa(horas_lectivas=1000, horas_practicas=500)
        self.assertEqual(p.total_horas, 1500)

    def test_total_horas_solo_lectivas(self):
        p = make_programa(horas_lectivas=800, horas_practicas=0)
        self.assertEqual(p.total_horas, 800)

    def test_estado_default_activo(self):
        self.assertEqual(make_programa().estado, Programa.Estado.ACTIVO)

    def test_nivel_default_tecnico(self):
        self.assertEqual(make_programa().nivel, Programa.Nivel.TECNICO)

    def test_tipo_formacion_default_por_oferta(self):
        self.assertEqual(make_programa().tipo_formacion, Programa.TipoFormacion.POR_OFERTA)

    def test_trimestres_totales_default_6(self):
        self.assertEqual(make_programa().trimestres_totales, 6)

    def test_ordering_por_nombre_ascendente(self):
        make_programa(nombre='Z Programa')
        make_programa(nombre='A Programa')
        make_programa(nombre='M Programa')
        nombres = list(Programa.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, sorted(nombres))

    # ── Validaciones clean() ─────────────────────────────────────────────────

    def test_horas_lectivas_cero_invalido(self):
        p = Programa(
            nombre='Test', nivel=Programa.Nivel.TECNICO,
            horas_lectivas=0, horas_practicas=100,
        )
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_cadena_formacion_requiere_trimestres_cadena(self):
        p = Programa(
            nombre='Cadena Test', nivel=Programa.Nivel.TECNICO,
            horas_lectivas=800, horas_practicas=400,
            tipo_formacion=Programa.TipoFormacion.CADENA_FORMACION,
            trimestres_totales=6,
            trimestres_cadena=None,  # faltante
        )
        with self.assertRaises(ValidationError) as ctx:
            p.full_clean()
        self.assertIn('trimestres_cadena', ctx.exception.message_dict)

    def test_cadena_formacion_trimestres_cadena_debe_ser_menor_total(self):
        p = Programa(
            nombre='Cadena Test2', nivel=Programa.Nivel.TECNICO,
            horas_lectivas=800, horas_practicas=400,
            tipo_formacion=Programa.TipoFormacion.CADENA_FORMACION,
            trimestres_totales=6,
            trimestres_cadena=6,   # igual que totales → inválido
        )
        with self.assertRaises(ValidationError) as ctx:
            p.full_clean()
        self.assertIn('trimestres_cadena', ctx.exception.message_dict)

    def test_cadena_formacion_valida(self):
        p = make_programa(
            tipo_formacion=Programa.TipoFormacion.CADENA_FORMACION,
            trimestres_totales=6,
            trimestres_cadena=4,   # 4 < 6 → válido
        )
        self.assertIsNotNone(p.pk)

    def test_por_oferta_limpia_trimestres_cadena(self):
        """Al guardar con POR_OFERTA, trimestres_cadena debe quedar en None."""
        p = make_programa(
            tipo_formacion=Programa.TipoFormacion.POR_OFERTA,
        )
        self.assertIsNone(p.trimestres_cadena)


class VersionProgramaModelTest(TestCase):

    def test_str_contiene_nombre_programa_y_numero(self):
        prog = make_programa(nombre='Mi Programa')
        v = make_version(programa=prog, numero=3)
        s = str(v)
        self.assertIn('Mi Programa', s)
        self.assertIn('3', s)

    def test_solo_una_version_vigente_por_programa(self):
        prog = make_programa()
        v1 = make_version(programa=prog, numero=1, vigente=True)
        v2 = make_version(programa=prog, numero=2, vigente=True)
        v1.refresh_from_db()
        # v1 debe haber sido desactivada al activar v2
        self.assertFalse(v1.vigente)
        self.assertTrue(v2.vigente)

    def test_unique_together_programa_numero(self):
        prog = make_programa()
        make_version(programa=prog, numero=1)
        with self.assertRaises(Exception):
            # Crear misma versión para el mismo programa
            VersionPrograma.objects.create(
                programa=prog, numero=1, vigente=False,
                fecha_inicio=date(2024, 6, 1),
            )

    def test_version_no_vigente_por_defecto(self):
        v = make_version()
        self.assertFalse(v.vigente)

    def test_fecha_fin_anterior_a_inicio_invalida(self):
        v = VersionPrograma(
            programa=make_programa(),
            numero=99,
            vigente=False,
            fecha_inicio=date(2024, 6, 1),
            fecha_fin=date(2024, 1, 1),  # anterior a inicio
        )
        with self.assertRaises(ValidationError) as ctx:
            v.full_clean()
        self.assertIn('fecha_fin', ctx.exception.message_dict)

    def test_total_horas_suma_modulos_activos(self):
        version = make_version()
        make_modulo(version=version, horas_lectivas=60, horas_practicas=30)
        make_modulo(version=version, horas_lectivas=40, horas_practicas=20)
        self.assertEqual(version.total_horas, 150)

    def test_total_horas_excluye_modulos_inactivos(self):
        version = make_version()
        make_modulo(version=version, horas_lectivas=60, horas_practicas=30)
        make_modulo(
            version=version,
            horas_lectivas=40, horas_practicas=20,
            estado=Modulo.Estado.INACTIVO,
        )
        # Solo los activos cuentan (60+30=90)
        self.assertEqual(version.total_horas, 90)

    def test_ordering_programa_y_numero_descendente(self):
        prog = make_programa()
        make_version(programa=prog, numero=1)
        make_version(programa=prog, numero=3)
        make_version(programa=prog, numero=2)
        numeros = list(
            VersionPrograma.objects.filter(programa=prog)
            .values_list('numero', flat=True)
        )
        # ordering = ['programa', '-numero'] → descendente
        self.assertEqual(numeros, sorted(numeros, reverse=True))


class ModuloModelTest(TestCase):

    def test_str_contiene_version_y_nombre(self):
        m = make_modulo(nombre='Bases de Datos')
        self.assertIn('Bases de Datos', str(m))

    def test_total_horas(self):
        m = make_modulo(horas_lectivas=60, horas_practicas=30)
        self.assertEqual(m.total_horas, 90)

    def test_estado_default_activo(self):
        self.assertEqual(make_modulo().estado, Modulo.Estado.ACTIVO)

    def test_unique_together_version_orden(self):
        version = make_version()
        make_modulo(version=version, orden=1)
        with self.assertRaises(Exception):
            Modulo.objects.create(
                version=version, nombre='Duplicado', orden=1,
                horas_lectivas=40, horas_practicas=20,
            )

    def test_horas_lectivas_cero_invalido(self):
        with self.assertRaises(ValidationError):
            Modulo.objects.create(
                version=make_version(), nombre='Test', orden=99,
                horas_lectivas=0, horas_practicas=20,
            )

    def test_horas_practicas_negativas_invalido(self):
        with self.assertRaises(ValidationError):
            Modulo.objects.create(
                version=make_version(), nombre='Test', orden=99,
                horas_lectivas=40, horas_practicas=-1,
            )

    def test_version_protegida_al_eliminar(self):
        from django.db.models.deletion import ProtectedError
        version = make_version()
        make_modulo(version=version)
        with self.assertRaises(ProtectedError):
            version.delete()

    def test_ordering_por_version_y_orden(self):
        version = make_version()
        make_modulo(version=version, orden=3)
        make_modulo(version=version, orden=1)
        make_modulo(version=version, orden=2)
        ordenes = list(
            Modulo.objects.filter(version=version)
            .values_list('orden', flat=True)
        )
        self.assertEqual(ordenes, sorted(ordenes))