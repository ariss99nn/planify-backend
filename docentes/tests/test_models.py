from django.test import TestCase
from docentes.tests.factories import make_docente, make_docente_user
from docentes.models.docente_model import Docente


class DocenteModelTest(TestCase):

    def test_str(self):
        docente = make_docente(especialidad='Física')
        self.assertIn('Física', str(docente))
        self.assertIn(docente.user.nombre, str(docente))

    def test_estado_default_true(self):
        docente = make_docente()
        self.assertTrue(docente.estado)

    def test_imagen_opcional(self):
        docente = make_docente()
        self.assertFalse(bool(docente.imagen))

    def test_relacion_user_one_to_one(self):
        docente = make_docente()
        self.assertEqual(docente.user.docente, docente)

    def test_no_puede_crear_dos_docentes_para_mismo_user(self):
        user = make_docente_user(email='único@test.com')
        make_docente(user=user)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Docente.objects.create(
                user=user,
                especialidad='Otra',
                horas_max_semanales=10,
            )

    def test_ordering_por_nombre_user(self):
        make_docente(user=make_docente_user(email='z@test.com', nombre='Zara'))
        make_docente(user=make_docente_user(email='a@test.com', nombre='Ana'))
        nombres = list(Docente.objects.values_list('user__nombre', flat=True))
        self.assertEqual(nombres, sorted(nombres))

    def test_horas_positivas(self):
        docente = make_docente(horas=40)
        self.assertEqual(docente.horas_max_semanales, 40)