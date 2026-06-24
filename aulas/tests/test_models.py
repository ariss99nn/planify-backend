from django.test import TestCase
from django.core.exceptions import ValidationError
from aulas.tests.factories import make_bloque, make_equipamiento, make_aula
from aulas.models.bloque_model import Bloque
from aulas.models.equipamiento_model import Equipamiento
from aulas.models.aula_model import Aula


class BloqueModelTest(TestCase):

    def test_str(self):
        bloque = make_bloque(nombre='Bloque Norte')
        self.assertEqual(str(bloque), 'Bloque Norte')

    def test_nombre_unico(self):
        make_bloque(nombre='Único')
        with self.assertRaises(Exception):
            Bloque.objects.create(nombre='Único', pisos=2, capacidad_maxima=100)

    def test_ordering_por_nombre(self):
        make_bloque(nombre='Z Bloque')
        make_bloque(nombre='A Bloque')
        nombres = list(Bloque.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, sorted(nombres))


class EquipamientoModelTest(TestCase):

    def test_str_incluye_estado(self):
        equip = make_equipamiento(nombre='Televisor')
        self.assertIn('Televisor', str(equip))
        self.assertIn('Funcional', str(equip))

    def test_estado_default_funcional(self):
        equip = make_equipamiento()
        self.assertEqual(equip.estado, Equipamiento.Estado.FUNCIONAL)

    def test_numero_serie_unico(self):
        make_equipamiento(nombre='Laptop A', numero_serie='SN-001')
        with self.assertRaises(Exception):
            Equipamiento.objects.create(
                nombre='Laptop B',
                cantidad=1,
                numero_serie='SN-001',
            )

    def test_imagen_opcional(self):
        equip = make_equipamiento()
        self.assertFalse(bool(equip.imagen))


class AulaModelTest(TestCase):

    def test_str(self):
        bloque = make_bloque(nombre='Bloque Sur')
        aula = make_aula(bloque=bloque, codigo='S201')
        self.assertIn('S201', str(aula))
        self.assertIn('Bloque Sur', str(aula))

    def test_estado_default_activa(self):
        aula = make_aula()
        self.assertEqual(aula.estado, Aula.Estado.ACTIVA)

    def test_codigo_unico(self):
        bloque = make_bloque()
        make_aula(bloque=bloque, codigo='X100')
        with self.assertRaises(Exception):
            Aula.objects.create(
                codigo_aula='X100',
                capacidad=30,
                tipo_aula=Aula.TipoAula.TEORICA,
                bloque=bloque,
            )

    def test_bloque_protegido_al_eliminar(self):
        from django.db import models
        from django.db.models.deletion import ProtectedError
        bloque = make_bloque()
        make_aula(bloque=bloque)
        with self.assertRaises(ProtectedError):
            bloque.delete()

    def test_equipamiento_many_to_many(self):
        aula = make_aula()
        eq1 = make_equipamiento(nombre='Proyector M2M')
        eq2 = make_equipamiento(nombre='Computador M2M')
        aula.equipamiento.set([eq1, eq2])
        self.assertEqual(aula.equipamiento.count(), 2)

    def test_imagen_opcional(self):
        aula = make_aula()
        self.assertFalse(bool(aula.imagen))