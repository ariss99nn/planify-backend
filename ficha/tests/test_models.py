from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from ficha.tests.factories import make_ficha, make_ficha_estudiante
from ficha.models.ficha_model import Ficha
from ficha.models.ficha_estudiante_model import FichaEstudiante
from ficha.models.ficha_historial_etapa_model import HistorialEtapa
from users.tests.factories import make_estudiante, make_docente


class FichaModelTest(TestCase):

    def test_str(self):
        ficha = make_ficha()
        self.assertIn('Ficha', str(ficha))
        self.assertIn(ficha.codigo_ficha, str(ficha))

    def test_estado_default_true(self):
        ficha = make_ficha()
        self.assertTrue(ficha.estado)

    def test_etapa_default_lectiva(self):
        ficha = make_ficha()
        self.assertEqual(ficha.etapa, Ficha.Etapa.LECTIVA)

    def test_numero_estudiantes_real_property(self):
        ficha = make_ficha()
        e1 = make_estudiante(email='e1@test.com')
        e2 = make_estudiante(email='e2@test.com')
        make_ficha_estudiante(ficha=ficha, estudiante=e1, activo=True)
        make_ficha_estudiante(ficha=ficha, estudiante=e2, activo=False)
        self.assertEqual(ficha.numero_estudiantes_real, 1)

    def test_fecha_fin_anterior_a_inicio_invalida(self):
        from programa.tests.factories import make_version
        version = make_version()
        ficha = Ficha(
            codigo_ficha='TEST-001',
            version=version,
            jornada=Ficha.Jornada.MANANA,
            etapa=Ficha.Etapa.LECTIVA,
            horas_semanales_objetivo=40,
            trimestre=1,
            numero_estudiantes_estimado=20,
            fecha_inicio=date(2024, 6, 1),
            fecha_finalizacion=date(2024, 1, 1),
        )
        with self.assertRaises(ValidationError):
            ficha.clean()

    def test_signal_crea_historial_al_cambiar_etapa(self):
        ficha = make_ficha(etapa=Ficha.Etapa.LECTIVA)
        self.assertEqual(HistorialEtapa.objects.filter(ficha=ficha).count(), 0)
        ficha.etapa = Ficha.Etapa.PRODUCTIVA
        ficha.save()
        self.assertEqual(HistorialEtapa.objects.filter(ficha=ficha).count(), 1)
        historial = HistorialEtapa.objects.get(ficha=ficha)
        self.assertEqual(historial.etapa_anterior, Ficha.Etapa.LECTIVA)
        self.assertEqual(historial.etapa_nueva, Ficha.Etapa.PRODUCTIVA)

    def test_signal_no_crea_historial_si_etapa_no_cambia(self):
        ficha = make_ficha(etapa=Ficha.Etapa.LECTIVA)
        ficha.trimestre = 2
        ficha.save()
        self.assertEqual(HistorialEtapa.objects.filter(ficha=ficha).count(), 0)

    def test_signal_registra_trimestre_en_historial(self):
        ficha = make_ficha(etapa=Ficha.Etapa.LECTIVA, trimestre=3)
        ficha.etapa = Ficha.Etapa.PRODUCTIVA
        ficha.save()
        historial = HistorialEtapa.objects.get(ficha=ficha)
        self.assertEqual(historial.trimestre, 3)


class FichaEstudianteModelTest(TestCase):

    def test_str(self):
        estudiante = make_estudiante(email='str_est@test.com')
        fe = make_ficha_estudiante(estudiante=estudiante)
        self.assertIn(estudiante.nombre, str(fe))

    def test_no_cadena_bloquea_segunda_ficha_activa(self):
        estudiante = make_estudiante(email='doble@test.com')
        ficha1 = make_ficha()
        ficha2 = make_ficha()
        make_ficha_estudiante(ficha=ficha1, estudiante=estudiante, es_cadena=False)
        with self.assertRaises(ValidationError):
            FichaEstudiante.objects.create(
                ficha=ficha2,
                estudiante=estudiante,
                activo=True,
                es_cadena=False,
            )

    def test_cadena_permite_multiples_fichas_activas(self):
        estudiante = make_estudiante(email='cadena@test.com')
        ficha1 = make_ficha()
        ficha2 = make_ficha()
        make_ficha_estudiante(ficha=ficha1, estudiante=estudiante, es_cadena=True)
        fe2 = FichaEstudiante.objects.create(
            ficha=ficha2,
            estudiante=estudiante,
            activo=True,
            es_cadena=True,
        )
        self.assertTrue(fe2.pk is not None)

    def test_desactivar_sin_fecha_retiro_invalido(self):
        estudiante = make_estudiante(email='retiro@test.com')
        fe = make_ficha_estudiante(estudiante=estudiante, activo=True)
        fe.activo = False
        with self.assertRaises(ValidationError):
            fe.full_clean()

    def test_desactivar_sin_motivo_invalido(self):
        estudiante = make_estudiante(email='motivo@test.com')
        fe = make_ficha_estudiante(estudiante=estudiante, activo=True)
        fe.activo = False
        fe.fecha_retiro = date(2024, 6, 1)
        with self.assertRaises(ValidationError):
            fe.full_clean()

    def test_desactivar_con_fecha_y_motivo_valido(self):
        estudiante = make_estudiante(email='ok_retiro@test.com')
        fe = make_ficha_estudiante(estudiante=estudiante, activo=True)
        fe.activo = False
        fe.fecha_retiro = date(2024, 6, 1)
        fe.motivo_retiro = FichaEstudiante.MotivoRetiro.DESERCION
        fe.full_clean()
        fe.save()
        fe.refresh_from_db()
        self.assertFalse(fe.activo)

    def test_unique_together_ficha_estudiante(self):
        estudiante = make_estudiante(email='unique@test.com')
        ficha = make_ficha()
        make_ficha_estudiante(ficha=ficha, estudiante=estudiante)
        with self.assertRaises(Exception):
            FichaEstudiante.objects.create(
                ficha=ficha,
                estudiante=estudiante,
                activo=True,
            )