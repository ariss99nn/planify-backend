from django.test import TestCase
from aulas.tests.factories import make_bloque, make_equipamiento, make_aula
from aulas.models.aula_model import Aula
from aulas.models.equipamiento_model import Equipamiento
from aulas.serializers import (
    BloqueCreateSerializer,
    BloqueUpdateSerializer,
    BloqueDetailSerializer,
    EquipamientoCreateSerializer,
    EquipamientoUpdateSerializer,
    AulaCreateSerializer,
    AulaUpdateSerializer,
    AulaEstadoSerializer,
    AulaDetailSerializer,
)


class BloqueSerializerTest(TestCase):

    def test_create_valido(self):
        data = {'nombre': 'Bloque Test', 'pisos': 4, 'capacidad_maxima': 300}
        s = BloqueCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        bloque = s.save()
        self.assertEqual(bloque.nombre, 'Bloque Test')

    def test_piso_cero_invalido(self):
        data = {'nombre': 'Bloque X', 'pisos': 0, 'capacidad_maxima': 100}
        s = BloqueCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('pisos', s.errors)

    def test_capacidad_cero_invalida(self):
        data = {'nombre': 'Bloque Y', 'pisos': 2, 'capacidad_maxima': 0}
        s = BloqueCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('capacidad_maxima', s.errors)

    def test_total_aulas_en_detail(self):
        bloque = make_bloque()
        make_aula(bloque=bloque)
        make_aula(bloque=bloque)
        data = BloqueDetailSerializer(bloque).data
        self.assertEqual(data['total_aulas'], 2)

    def test_update_parcial(self):
        bloque = make_bloque(nombre='Original')
        s = BloqueUpdateSerializer(bloque, data={'pisos': 5}, partial=True)
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        bloque.refresh_from_db()
        self.assertEqual(bloque.pisos, 5)


class EquipamientoSerializerTest(TestCase):

    def test_create_valido(self):
        data = {
            'nombre': 'Computador Sala',
            'cantidad': 10,
            'estado': Equipamiento.Estado.FUNCIONAL,
        }
        s = EquipamientoCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        equip = s.save()
        self.assertEqual(equip.cantidad, 10)

    def test_cantidad_cero_invalida(self):
        data = {'nombre': 'Silla', 'cantidad': 0}
        s = EquipamientoCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('cantidad', s.errors)

    def test_estado_display_en_detail(self):
        equip = make_equipamiento(estado=Equipamiento.Estado.DAÑADO)
        from aulas.serializers import EquipamientoDetailSerializer
        data = EquipamientoDetailSerializer(equip).data
        self.assertEqual(data['estado_display'], 'Dañado')

    def test_numero_serie_opcional(self):
        data = {'nombre': 'Mesa sin serie', 'cantidad': 5}
        s = EquipamientoCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)


class AulaSerializerTest(TestCase):

    def setUp(self):
        self.bloque = make_bloque()

    def test_create_valido(self):
        data = {
            'codigo_aula': 'B101',
            'capacidad': 35,
            'tipo_aula': Aula.TipoAula.TEORICA,
            'bloque': self.bloque.pk,
        }
        s = AulaCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        aula = s.save()
        self.assertEqual(aula.codigo_aula, 'B101')

    def test_codigo_se_normaliza_uppercase(self):
        data = {
            'codigo_aula': 'b202',
            'capacidad': 30,
            'tipo_aula': Aula.TipoAula.LABORATORIO,
            'bloque': self.bloque.pk,
        }
        s = AulaCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        aula = s.save()
        self.assertEqual(aula.codigo_aula, 'B202')

    def test_capacidad_cero_invalida(self):
        data = {
            'codigo_aula': 'C101',
            'capacidad': 0,
            'tipo_aula': Aula.TipoAula.TEORICA,
            'bloque': self.bloque.pk,
        }
        s = AulaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('capacidad', s.errors)

    def test_create_con_equipamiento(self):
        eq = make_equipamiento(nombre='Proyector Aula')
        data = {
            'codigo_aula': 'D101',
            'capacidad': 40,
            'tipo_aula': Aula.TipoAula.SISTEMAS,
            'bloque': self.bloque.pk,
            'equipamiento': [eq.pk],
        }
        s = AulaCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        aula = s.save()
        self.assertEqual(aula.equipamiento.count(), 1)

    def test_estado_serializer_valido(self):
        aula = make_aula(bloque=self.bloque)
        s = AulaEstadoSerializer(aula, data={'estado': Aula.Estado.MANTENIMIENTO})
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        aula.refresh_from_db()
        self.assertEqual(aula.estado, Aula.Estado.MANTENIMIENTO)

    def test_estado_invalido(self):
        aula = make_aula(bloque=self.bloque)
        s = AulaEstadoSerializer(aula, data={'estado': 'INVALIDO'})
        self.assertFalse(s.is_valid())

    def test_detail_serializer_bloque_anidado(self):
        aula = make_aula(bloque=self.bloque)
        data = AulaDetailSerializer(aula).data
        self.assertIn('bloque', data)
        self.assertIn('nombre', data['bloque'])

    def test_detail_serializer_equipamiento_anidado(self):
        aula = make_aula(bloque=self.bloque)
        eq = make_equipamiento(nombre='TV Sala')
        aula.equipamiento.add(eq)
        data = AulaDetailSerializer(aula).data
        self.assertEqual(len(data['equipamiento']), 1)
        self.assertEqual(data['equipamiento'][0]['nombre'], 'TV Sala')