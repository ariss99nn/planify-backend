from django.test import TestCase, RequestFactory
from docentes.tests.factories import make_docente, make_docente_user, make_docente_inactivo
from docentes.serializers import (
    DocenteCreateSerializer,
    DocenteListSerializer,
    DocenteDetailSerializer,
    DocenteUpdateSerializer,
    DocenteDeactivateSerializer,
)
from users.models.user import User
from users.tests.factories import make_user


class DocenteCreateSerializerTest(TestCase):

    def test_create_valido(self):
        user = make_docente_user(email='nuevo@test.com')
        data = {
            'user_id': user.pk,
            'especialidad': 'Química',
            'horas_max_semanales': 20,
            'estado': True,
        }
        serializer = DocenteCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        docente = serializer.save()
        self.assertEqual(docente.user, user)
        self.assertEqual(docente.especialidad, 'Química')

    def test_user_ya_tiene_perfil(self):
        user = make_docente_user(email='yaexiste@test.com')
        make_docente(user=user)
        data = {
            'user_id': user.pk,
            'especialidad': 'Historia',
            'horas_max_semanales': 10,
        }
        serializer = DocenteCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_id', serializer.errors)

    def test_user_rol_incorrecto(self):
        estudiante = make_user(rol=User.Rol.ESTUDIANTE, email='est@test.com')
        data = {
            'user_id': estudiante.pk,
            'especialidad': 'Arte',
            'horas_max_semanales': 10,
        }
        serializer = DocenteCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_user_inactivo_rechazado(self):
        user = make_docente_user(email='inactivo@test.com', estado=False)
        data = {
            'user_id': user.pk,
            'especialidad': 'Arte',
            'horas_max_semanales': 10,
        }
        serializer = DocenteCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_horas_cero_invalido(self):
        user = make_docente_user(email='horas@test.com')
        data = {
            'user_id': user.pk,
            'especialidad': 'Música',
            'horas_max_semanales': 0,
        }
        serializer = DocenteCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('horas_max_semanales', serializer.errors)

    def test_horas_sobre_40_invalido(self):
        user = make_docente_user(email='horas2@test.com')
        data = {
            'user_id': user.pk,
            'especialidad': 'Música',
            'horas_max_semanales': 41,
        }
        serializer = DocenteCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('horas_max_semanales', serializer.errors)

    def test_horas_exactamente_40_valido(self):
        user = make_docente_user(email='horas3@test.com')
        data = {
            'user_id': user.pk,
            'especialidad': 'Educación Física',
            'horas_max_semanales': 40,
        }
        serializer = DocenteCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class DocenteListSerializerTest(TestCase):

    def test_campos_esperados(self):
        docente = make_docente()
        data = DocenteListSerializer(docente).data
        for campo in ['id', 'nombre', 'email', 'especialidad', 'horas_max_semanales', 'estado']:
            self.assertIn(campo, data)

    def test_nombre_viene_de_user(self):
        user = make_docente_user(email='nombre@test.com', nombre='Diana Test')
        docente = make_docente(user=user)
        data = DocenteListSerializer(docente).data
        self.assertEqual(data['nombre'], 'Diana Test')

    def test_email_viene_de_user(self):
        user = make_docente_user(email='email@test.com')
        docente = make_docente(user=user)
        data = DocenteListSerializer(docente).data
        self.assertEqual(data['email'], 'email@test.com')


class DocenteDetailSerializerTest(TestCase):

    def test_user_anidado(self):
        docente = make_docente()
        data = DocenteDetailSerializer(docente).data
        self.assertIn('user', data)
        self.assertIn('email', data['user'])
        self.assertIn('rol', data['user'])

    def test_campos_docente_presentes(self):
        docente = make_docente(especialidad='Biología', horas=25)
        data = DocenteDetailSerializer(docente).data
        self.assertEqual(data['especialidad'], 'Biología')
        self.assertEqual(data['horas_max_semanales'], 25)


class DocenteUpdateSerializerTest(TestCase):

    def test_update_parcial(self):
        docente = make_docente(especialidad='Inglés', horas=15)
        serializer = DocenteUpdateSerializer(
            docente,
            data={'especialidad': 'Inglés Avanzado'},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        docente.refresh_from_db()
        self.assertEqual(docente.especialidad, 'Inglés Avanzado')
        self.assertEqual(docente.horas_max_semanales, 15)

    def test_no_puede_cambiar_user(self):
        docente = make_docente()
        otro_user = make_docente_user(email='otro@test.com')
        serializer = DocenteUpdateSerializer(
            docente,
            data={'user_id': otro_user.pk, 'especialidad': 'Arte'},
            partial=True,
        )
        serializer.is_valid()
        serializer.save()
        docente.refresh_from_db()
        self.assertNotEqual(docente.user, otro_user)


class DocenteDeactivateSerializerTest(TestCase):

    def test_desactiva_docente_y_user(self):
        docente = make_docente()
        self.assertTrue(docente.estado)
        self.assertTrue(docente.user.estado)

        serializer = DocenteDeactivateSerializer(
            docente,
            data={'confirmacion': True},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        docente.refresh_from_db()
        docente.user.refresh_from_db()
        self.assertFalse(docente.estado)
        self.assertFalse(docente.user.estado)

    def test_confirmacion_false_invalido(self):
        docente = make_docente()
        serializer = DocenteDeactivateSerializer(
            docente,
            data={'confirmacion': False},
        )
        self.assertFalse(serializer.is_valid())

    def test_registro_no_se_elimina(self):
        from docentes.models.docente_model import Docente
        docente = make_docente()
        pk = docente.pk
        serializer = DocenteDeactivateSerializer(
            docente,
            data={'confirmacion': True},
        )
        serializer.is_valid()
        serializer.save()
        self.assertTrue(Docente.objects.filter(pk=pk).exists())