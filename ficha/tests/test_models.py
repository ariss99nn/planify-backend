from datetime import date, time
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse

from users.tests.factories import (
    make_coordinador, make_docente as make_user_docente,
    make_estudiante, make_user, get_auth_header,
)
from docentes.tests.factories import make_docente, make_docente_user
from ficha.tests.factories import make_ficha, make_ficha_estudiante, make_reasignacion
from programa.tests.factories import make_programa, make_version, make_modulo, make_docente_modulo
from competencia.tests.factories import make_asignatura, make_competencia, make_rap, make_docente_asignatura
from aulas.tests import make_aula, make_bloque as make_bloque_aulas, make_equipamiento
from bhorario.tests.factories import make_bloque

from ficha.models.ficha_model import Ficha
from ficha.models.ficha_estudiante_model import FichaEstudiante
from ficha.models.ficha_historial_etapa_model import HistorialEtapa
from aulas.models.aula_model import Aula
from aulas.models.bloque_model import Bloque
from aulas.models.equipamiento_model import Equipamiento
from competencia.models.asignatura_model import Asignatura
from competencia.models.competencia_model import Competencia
from programa.models.programa_model import Programa
from programa.models.modulo_model import Modulo

BASE = '/api/v1'

class FichaModelTest(TestCase):

    def test_str_contiene_codigo_ficha(self):
        ficha = make_ficha()
        self.assertIn(ficha.codigo_ficha, str(ficha))

    def test_estado_default_true(self):
        self.assertTrue(make_ficha().estado)

    def test_etapa_default_lectiva(self):
        self.assertEqual(make_ficha().etapa, Ficha.Etapa.LECTIVA)

    def test_numero_estudiantes_real_cuenta_solo_activos(self):
        ficha = make_ficha()
        e1 = make_estudiante(email='e1@t.com')
        e2 = make_estudiante(email='e2@t.com')
        make_ficha_estudiante(ficha=ficha, estudiante=e1, activo=True)
        make_ficha_estudiante(ficha=ficha, estudiante=e2, activo=False)
        self.assertEqual(ficha.numero_estudiantes_real, 1)

    def test_fecha_fin_anterior_a_inicio_invalida(self):
        from programa.tests.factories import make_version
        ficha = Ficha(
            codigo_ficha='TEST-001',
            version=make_version(),
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
        h = HistorialEtapa.objects.get(ficha=ficha)
        self.assertEqual(h.etapa_anterior, Ficha.Etapa.LECTIVA)
        self.assertEqual(h.etapa_nueva, Ficha.Etapa.PRODUCTIVA)

    def test_signal_no_crea_historial_si_etapa_no_cambia(self):
        ficha = make_ficha(etapa=Ficha.Etapa.LECTIVA)
        ficha.trimestre = 2
        ficha.save()
        self.assertEqual(HistorialEtapa.objects.filter(ficha=ficha).count(), 0)

    def test_signal_registra_trimestre_en_historial(self):
        ficha = make_ficha(etapa=Ficha.Etapa.LECTIVA, trimestre=3)
        ficha.etapa = Ficha.Etapa.PRODUCTIVA
        ficha.save()
        h = HistorialEtapa.objects.get(ficha=ficha)
        self.assertEqual(h.trimestre, 3)

    def test_codigo_ficha_unico(self):
        make_ficha(codigo='UNICO-001')
        with self.assertRaises(Exception):
            Ficha.objects.create(
                codigo_ficha='UNICO-001',
                version=make_version(),
                jornada=Ficha.Jornada.MANANA,
                etapa=Ficha.Etapa.LECTIVA,
                horas_semanales_objetivo=40,
                trimestre=1,
                numero_estudiantes_estimado=20,
                fecha_inicio=date(2024, 1, 1),
            )



class FichaEstudianteModelTest(TestCase):

    def test_str_contiene_nombre_estudiante(self):
        est = make_estudiante(email='str@t.com')
        fe = make_ficha_estudiante(estudiante=est)
        self.assertIn(est.nombre, str(fe))

    def test_no_cadena_bloquea_segunda_ficha_activa(self):
        est = make_estudiante(email='doble@t.com')
        ficha1 = make_ficha()
        ficha2 = make_ficha()
        make_ficha_estudiante(ficha=ficha1, estudiante=est, es_cadena=False)
        with self.assertRaises(ValidationError):
            FichaEstudiante.objects.create(
                ficha=ficha2, estudiante=est, activo=True, es_cadena=False,
            )

    def test_cadena_permite_multiples_fichas_activas(self):
        est = make_estudiante(email='cadena@t.com')
        fe2 = FichaEstudiante.objects.create(
            ficha=make_ficha(), estudiante=est, activo=True, es_cadena=True,
        )
        self.assertIsNotNone(fe2.pk)

    def test_desactivar_sin_fecha_retiro_invalido(self):
        est = make_estudiante(email='retiro@t.com')
        fe = make_ficha_estudiante(estudiante=est, activo=True)
        fe.activo = False
        with self.assertRaises(ValidationError):
            fe.full_clean()

    def test_desactivar_sin_motivo_invalido(self):
        est = make_estudiante(email='motivo@t.com')
        fe = make_ficha_estudiante(estudiante=est, activo=True)
        fe.activo = False
        fe.fecha_retiro = date(2024, 6, 1)
        with self.assertRaises(ValidationError):
            fe.full_clean()

    def test_desactivar_con_fecha_y_motivo_valido(self):
        est = make_estudiante(email='ok@t.com')
        fe = make_ficha_estudiante(estudiante=est, activo=True)
        fe.activo = False
        fe.fecha_retiro = date(2024, 6, 1)
        fe.motivo_retiro = FichaEstudiante.MotivoRetiro.DESERCION
        fe.full_clean()
        fe.save()
        fe.refresh_from_db()
        self.assertFalse(fe.activo)

    def test_unique_together_ficha_estudiante(self):
        est = make_estudiante(email='unique@t.com')
        ficha = make_ficha()
        make_ficha_estudiante(ficha=ficha, estudiante=est)
        with self.assertRaises(Exception):
            FichaEstudiante.objects.create(ficha=ficha, estudiante=est, activo=True)


# ─────────────────────────────────────────────────────────────────────────────
# FICHA — Vistas
# ─────────────────────────────────────────────────────────────────────────────


