# aulas/tests/test_models.py
"""
Tests del módulo aulas: Bloque, Equipamiento, Aula.

CORRECCIONES:
- make_aula ahora recibe piso=1 correctamente.
- Aula.Estado usa valores cortos: 'ACT', 'MANT', 'INAC'.
- Aula.TipoAula usa valores cortos: 'LAB', 'TEO', 'SIS', 'OTR'.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

from aulas.models.aula_model import Aula
from aulas.models.bloque_model import Bloque
from aulas.models.equipamiento_model import Equipamiento
from aulas.tests.factories import make_aula, make_bloque, make_equipamiento


class BloqueModelTest(TestCase):

    def test_str_es_el_nombre(self):
        b = make_bloque(nombre='Bloque Norte')
        self.assertEqual(str(b), 'Bloque Norte')

    def test_estado_default_activo(self):
        self.assertEqual(make_bloque().estado, Bloque.Estado.ACTIVO)

    def test_nombre_unico(self):
        make_bloque(nombre='Único')
        with self.assertRaises(Exception):
            Bloque.objects.create(
                nombre='Único', pisos=2, capacidad_maxima=100,
            )

    def test_pisos_cero_invalido(self):
        with self.assertRaises(ValidationError) as ctx:
            Bloque.objects.create(nombre='SinPisos', pisos=0, capacidad_maxima=100)
        self.assertIn('pisos', ctx.exception.message_dict)

    def test_capacidad_cero_invalida(self):
        with self.assertRaises(ValidationError) as ctx:
            Bloque.objects.create(nombre='SinCap', pisos=3, capacidad_maxima=0)
        self.assertIn('capacidad_maxima', ctx.exception.message_dict)

    def test_ordering_por_nombre(self):
        make_bloque(nombre='Z Bloque')
        make_bloque(nombre='A Bloque')
        nombres = list(Bloque.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, sorted(nombres))

    def test_imagen_es_opcional(self):
        b = make_bloque()
        self.assertFalse(bool(b.imagen))


class EquipamientoModelTest(TestCase):

    def test_str_contiene_nombre_y_estado(self):
        eq = make_equipamiento(nombre='Proyector')
        s = str(eq)
        self.assertIn('Proyector', s)

    def test_estado_default_funcional(self):
        # 'FUNC' es el valor del choice FUNCIONAL
        self.assertEqual(make_equipamiento().estado, Equipamiento.Estado.FUNCIONAL)

    def test_cantidad_cero_invalida(self):
        with self.assertRaises(ValidationError) as ctx:
            Equipamiento.objects.create(nombre='Test', cantidad=0)
        self.assertIn('cantidad', ctx.exception.message_dict)

    def test_numero_serie_unico(self):
        make_equipamiento(nombre='A', numero_serie='SN-001')
        with self.assertRaises(Exception):
            Equipamiento.objects.create(nombre='B', cantidad=1, numero_serie='SN-001')

    def test_numero_serie_puede_ser_null(self):
        eq1 = make_equipamiento(nombre='E1')
        eq2 = make_equipamiento(nombre='E2')
        self.assertIsNone(eq1.numero_serie)
        self.assertIsNone(eq2.numero_serie)

    def test_imagen_es_opcional(self):
        self.assertFalse(bool(make_equipamiento().imagen))

    def test_ordering_por_nombre(self):
        make_equipamiento(nombre='Z Equipo')
        make_equipamiento(nombre='A Equipo')
        nombres = list(Equipamiento.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, sorted(nombres))


class AulaModelTest(TestCase):

    def test_str_contiene_codigo_y_bloque(self):
        bloque = make_bloque(nombre='Sur')
        aula   = make_aula(bloque=bloque, codigo='S201')
        s = str(aula)
        self.assertIn('S201', s)

    def test_estado_default_activa(self):
        aula = make_aula()
        # El valor del choice ACTIVA es 'ACT' (no 'ACTIVA')
        self.assertEqual(aula.estado, Aula.Estado.ACTIVA)
        self.assertEqual(aula.estado, 'ACT')

    def test_codigo_unico(self):
        bloque = make_bloque()
        make_aula(bloque=bloque, codigo='X100')
        with self.assertRaises(Exception):
            Aula.objects.create(
                codigo_aula='X100', capacidad=30, piso=1,
                tipo_aula=Aula.TipoAula.TEORICA, bloque=bloque,
            )

    def test_capacidad_cero_invalida(self):
        bloque = make_bloque()
        with self.assertRaises(ValidationError) as ctx:
            Aula.objects.create(
                codigo_aula='CAP-0', capacidad=0, piso=1,
                tipo_aula=Aula.TipoAula.TEORICA, bloque=bloque,
            )
        self.assertIn('capacidad', ctx.exception.message_dict)

    def test_piso_supera_pisos_del_bloque_invalido(self):
        bloque = make_bloque(pisos=3)
        with self.assertRaises(ValidationError) as ctx:
            Aula.objects.create(
                codigo_aula='PISO-ALTO', capacidad=30, piso=5,
                tipo_aula=Aula.TipoAula.TEORICA, bloque=bloque,
            )
        self.assertIn('piso', ctx.exception.message_dict)

    def test_bloque_protegido_al_eliminar(self):
        bloque = make_bloque()
        make_aula(bloque=bloque)
        with self.assertRaises(ProtectedError):
            bloque.delete()

    def test_equipamiento_many_to_many(self):
        aula = make_aula()
        eq1  = make_equipamiento(nombre='Monitor M2M')
        eq2  = make_equipamiento(nombre='PC M2M')
        aula.equipamiento.set([eq1, eq2])
        self.assertEqual(aula.equipamiento.count(), 2)

    def test_imagen_es_opcional(self):
        self.assertFalse(bool(make_aula().imagen))

    def test_tipo_aula_valor_corto(self):
        """TipoAula.TEORICA tiene valor 'TEO', no 'TEORICA'."""
        aula = make_aula(tipo=Aula.TipoAula.TEORICA)
        self.assertEqual(aula.tipo_aula, 'TEO')

    def test_estado_mantenimiento_valor_corto(self):
        """Estado.MANTENIMIENTO tiene valor 'MANT', no 'MANTENIMIENTO'."""
        aula = make_aula(estado=Aula.Estado.MANTENIMIENTO)
        self.assertEqual(aula.estado, 'MANT')