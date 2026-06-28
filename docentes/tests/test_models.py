from datetime import date, time
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from users.tests.factories import (
    make_coordinador, make_docente as make_user_docente,
    make_estudiante, make_user, get_auth_header,
)
from docentes.tests.factories import make_docente, make_docente_user, make_docente_inactivo
from bhorario.tests.factories import make_bloque
from planificacion.tests.factories import make_plan, make_item
from ficha.tests.factories import make_ficha
from competencia.tests.factories import make_competencia, make_asignatura
from aulas.tests import make_aula

from bhorario.models.bloque_horario_model import BloqueHorario
from bhorario.services.bloque_service import BloqueHorarioService, ColisionError
from planificacion.models.plan_trimestral_model import PlanTrimestral
from docentes.models.docente_model import Docente

BASE = '/api/v1'

class DocenteModelTest(TestCase):

    def test_str_contiene_nombre_y_especialidad(self):
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
        user = make_docente_user(email='unico@test.com')
        make_docente(user=user)
        with self.assertRaises(IntegrityError):
            Docente.objects.create(
                user=user, especialidad='Otra', horas_max_semanales=10,
            )

    def test_ordering_por_nombre_user(self):
        make_docente(user=make_docente_user(email='z@test.com', nombre='Zara'))
        make_docente(user=make_docente_user(email='a@test.com', nombre='Ana'))
        nombres = list(Docente.objects.values_list('user__nombre', flat=True))
        self.assertEqual(nombres, sorted(nombres))

    def test_horas_max_semanales_positivas(self):
        docente = make_docente(horas=40)
        self.assertEqual(docente.horas_max_semanales, 40)

    def test_horas_max_efectivas_sin_extra(self):
        docente = make_docente(horas=40)
        docente.permite_horas_extra = False
        docente.save()
        self.assertEqual(docente.horas_max_efectivas, 40)

    def test_horas_max_efectivas_con_extra(self):
        docente = make_docente(horas=40)
        docente.permite_horas_extra = True
        docente.horas_extra_autorizadas = 4
        docente.save()
        self.assertEqual(docente.horas_max_efectivas, 44)

    def test_clean_horas_extra_sin_permitir_falla(self):
        """No se puede definir horas_extra_autorizadas sin permite_horas_extra=True."""
        docente = make_docente(horas=40)
        docente.permite_horas_extra = False
        docente.horas_extra_autorizadas = 4
        with self.assertRaises(ValidationError):
            docente.clean()



class DisponibilidadModelTest(TestCase):

    def setUp(self):
        self.docente = make_docente(email='disp@test.com')

    def _make_disp(self, **kwargs):
        from docentes.models.docente_disponibilidad_model import Disponibilidad
        defaults = {
            'docente': self.docente,
            'dia_semana': BloqueHorario.DiaSemana.LUNES,
            'hora_inicio': time(6, 0),
            'hora_fin': time(8, 0),
            'disponible': True,
            'tipo_restriccion': 'PERMANENTE',
        }
        defaults.update(kwargs)
        return Disponibilidad.objects.create(**defaults)

    def test_crear_disponibilidad_permanente(self):
        disp = self._make_disp()
        self.assertEqual(disp.tipo_restriccion, 'PERMANENTE')

    def test_hora_inicio_mayor_hora_fin_invalida(self):
        from docentes.models.docente_disponibilidad_model import Disponibilidad
        disp = Disponibilidad(
            docente=self.docente,
            dia_semana=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(10, 0), hora_fin=time(8, 0),
            tipo_restriccion='PERMANENTE',
        )
        with self.assertRaises(ValidationError):
            disp.clean()

    def test_restriccion_temporal_sin_fechas_invalida(self):
        from docentes.models.docente_disponibilidad_model import Disponibilidad
        disp = Disponibilidad(
            docente=self.docente,
            dia_semana=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
            tipo_restriccion='TEMPORAL',
            # Sin fecha_inicio_restriccion ni fecha_fin_restriccion
        )
        with self.assertRaises(ValidationError):
            disp.clean()



class HabilitacionDocenteModelTest(TestCase):

    def setUp(self):
        self.docente = make_docente(email='hab@test.com')
        self.asignatura = make_asignatura()

    def test_crear_habilitacion_por_asignatura(self):
        from docentes.models.docente_habilitacion_model import HabilitacionDocente
        hab = HabilitacionDocente.objects.create(
            docente=self.docente,
            asignatura=self.asignatura,
            activo=True,
        )
        self.assertTrue(hab.activo)

    def test_habilitacion_unica_por_docente_asignatura(self):
        from docentes.models.docente_habilitacion_model import HabilitacionDocente
        HabilitacionDocente.objects.create(
            docente=self.docente,
            asignatura=self.asignatura,
            activo=True,
        )
        with self.assertRaises(IntegrityError):
            HabilitacionDocente.objects.create(
                docente=self.docente,
                asignatura=self.asignatura,
                activo=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Docentes — Vistas
# ─────────────────────────────────────────────────────────────────────────────


