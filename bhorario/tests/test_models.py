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

class BloqueHorarioModelTest(TestCase):

    def test_str_contiene_hora_inicio_y_fin(self):
        bloque = make_bloque(hora_inicio=time(8, 0), hora_fin=time(10, 0))
        self.assertIn('08:00', str(bloque))
        self.assertIn('10:00', str(bloque))

    def test_hora_inicio_mayor_hora_fin_invalido(self):
        aula = make_aula()
        bloque = BloqueHorario(
            dia_semana=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(10, 0),
            hora_fin=time(8, 0),
            jornada=BloqueHorario.Jornada.MANANA,
            aula=aula,
        )
        with self.assertRaises(ValidationError):
            bloque.clean()

    def test_hora_inicio_igual_hora_fin_invalido(self):
        aula = make_aula()
        bloque = BloqueHorario(
            dia_semana=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(8, 0),
            hora_fin=time(8, 0),
            jornada=BloqueHorario.Jornada.MANANA,
            aula=aula,
        )
        with self.assertRaises(ValidationError):
            bloque.clean()

    def test_conflicto_docente_solapamiento_parcial(self):
        docente = make_docente(email='conf1@test.com')
        make_bloque(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(8, 0), hora_fin=time(10, 0),
            docente=docente,
        )
        bloque2 = BloqueHorario(
            dia_semana=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(9, 0), hora_fin=time(11, 0),
            jornada=BloqueHorario.Jornada.MANANA,
            docente=docente,
        )
        with self.assertRaises(ValidationError):
            bloque2.clean()

    def test_conflicto_docente_solapamiento_contenido(self):
        """Un bloque contenido dentro de otro también es conflicto."""
        docente = make_docente(email='conf2@test.com')
        make_bloque(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0), hora_fin=time(10, 0),
            docente=docente,
        )
        bloque2 = BloqueHorario(
            dia_semana=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(7, 0), hora_fin=time(9, 0),
            jornada=BloqueHorario.Jornada.MANANA,
            docente=docente,
        )
        with self.assertRaises(ValidationError):
            bloque2.clean()

    def test_conflicto_aula(self):
        aula = make_aula()
        make_bloque(
            dia=BloqueHorario.DiaSemana.MARTES,
            hora_inicio=time(8, 0), hora_fin=time(10, 0),
            aula=aula,
        )
        bloque2 = BloqueHorario(
            dia_semana=BloqueHorario.DiaSemana.MARTES,
            hora_inicio=time(9, 0), hora_fin=time(11, 0),
            jornada=BloqueHorario.Jornada.MANANA,
            aula=aula,
        )
        with self.assertRaises(ValidationError):
            bloque2.clean()

    def test_mismo_docente_dias_distintos_es_valido(self):
        docente = make_docente(email='dias@test.com')
        make_bloque(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(8, 0), hora_fin=time(10, 0),
            docente=docente,
        )
        bloque2 = BloqueHorario(
            dia_semana=BloqueHorario.DiaSemana.MARTES,
            hora_inicio=time(8, 0), hora_fin=time(10, 0),
            jornada=BloqueHorario.Jornada.MANANA,
            docente=docente,
        )
        bloque2.clean()  # No debe lanzar

    def test_mismo_docente_horas_contiguas_es_valido(self):
        """Fin de bloque 1 == inicio de bloque 2 no es solapamiento."""
        docente = make_docente(email='contig@test.com')
        make_bloque(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
            docente=docente,
        )
        bloque2 = BloqueHorario(
            dia_semana=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(8, 0), hora_fin=time(10, 0),
            jornada=BloqueHorario.Jornada.MANANA,
            docente=docente,
        )
        bloque2.clean()  # No debe lanzar

    def test_ordering_por_dia_y_hora(self):
        make_bloque(
            dia=BloqueHorario.DiaSemana.MIERCOLES,
            hora_inicio=time(14, 0), hora_fin=time(16, 0),
        )
        make_bloque(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
        )
        dias = list(BloqueHorario.objects.values_list('dia_semana', flat=True))
        self.assertEqual(dias, sorted(dias))


# ─────────────────────────────────────────────────────────────────────────────
# BloqueHorarioService — Tests del service (lógica de negocio)
# ─────────────────────────────────────────────────────────────────────────────


