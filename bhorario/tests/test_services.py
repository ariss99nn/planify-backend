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

class BloqueHorarioServiceTest(TestCase):
    """
    Tests del service corregido que incluye consulta a Disponibilidad.
    Cubre Bugs #1 y #6 de la auditoría de lógica.
    """

    def setUp(self):
        self.docente = make_docente(email='svc@test.com')
        self.aula = make_aula()
        self.ficha = make_ficha()

    def test_crear_bloque_exitoso(self):
        bloque = BloqueHorarioService.crear_bloque({
            'dia_semana':  BloqueHorario.DiaSemana.LUNES,
            'hora_inicio': time(6, 0),
            'hora_fin':    time(8, 0),
            'jornada':     BloqueHorario.Jornada.MANANA,
            'docente':     self.docente,
            'aula':        self.aula,
            'ficha':       self.ficha,
        })
        self.assertIsNotNone(bloque.pk)
        self.assertEqual(bloque.docente, self.docente)
        self.assertEqual(bloque.aula, self.aula)

    def test_crear_bloque_con_colision_lanza_colision_error(self):
        BloqueHorarioService.crear_bloque({
            'dia_semana':  BloqueHorario.DiaSemana.LUNES,
            'hora_inicio': time(6, 0), 'hora_fin': time(8, 0),
            'jornada':     BloqueHorario.Jornada.MANANA,
            'docente':     self.docente,
        })
        with self.assertRaises(ColisionError):
            BloqueHorarioService.crear_bloque({
                'dia_semana':  BloqueHorario.DiaSemana.LUNES,
                'hora_inicio': time(7, 0), 'hora_fin': time(9, 0),
                'jornada':     BloqueHorario.Jornada.MANANA,
                'docente':     self.docente,
            })

    def test_verificar_disponibilidad_retorna_disponible_true(self):
        resultado = BloqueHorarioService.verificar_disponibilidad(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
            docente=self.docente, aula=self.aula, ficha=self.ficha,
        )
        self.assertTrue(resultado['disponible'])
        self.assertEqual(resultado['conflictos'], [])

    def test_verificar_disponibilidad_docente_ocupado(self):
        BloqueHorarioService.crear_bloque({
            'dia_semana':  BloqueHorario.DiaSemana.LUNES,
            'hora_inicio': time(6, 0), 'hora_fin': time(8, 0),
            'jornada':     BloqueHorario.Jornada.MANANA,
            'docente':     self.docente,
        })
        resultado = BloqueHorarioService.verificar_disponibilidad(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(7, 0), hora_fin=time(9, 0),
            docente=self.docente,
        )
        self.assertFalse(resultado['disponible'])
        self.assertFalse(resultado['docente_disponible'])
        self.assertTrue(len(resultado['conflictos']) > 0)

    def test_verificar_disponibilidad_respeta_modelo_disponibilidad(self):
        """Bug #1 RESUELTO: verificar_disponibilidad consulta el modelo Disponibilidad."""
        from docentes.models.docente_disponibilidad_model import Disponibilidad
        Disponibilidad.objects.create(
            docente=self.docente,
            dia_semana=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0),
            hora_fin=time(8, 0),
            disponible=False,
            tipo_restriccion='PERMANENTE',
        )
        resultado = BloqueHorarioService.verificar_disponibilidad(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
            docente=self.docente,
        )
        self.assertFalse(resultado['disponible'])
        self.assertFalse(resultado['docente_disponible'])

    def test_verificar_disponibilidad_restriccion_temporal_fuera_rango_ignora(self):
        """Bug #6 RESUELTO: restricción TEMPORAL fuera del rango de fechas es ignorada."""
        from docentes.models.docente_disponibilidad_model import Disponibilidad
        from django.utils import timezone
        from datetime import timedelta

        ayer = timezone.now().date() - timedelta(days=30)
        hace_15 = timezone.now().date() - timedelta(days=15)

        Disponibilidad.objects.create(
            docente=self.docente,
            dia_semana=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0),
            hora_fin=time(8, 0),
            disponible=False,
            tipo_restriccion='TEMPORAL',
            fecha_inicio_restriccion=ayer,
            fecha_fin_restriccion=hace_15,  # Ya terminó
        )
        resultado = BloqueHorarioService.verificar_disponibilidad(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
            docente=self.docente,
        )
        # La restricción expiró → slot disponible
        self.assertTrue(resultado['disponible'])

    def test_verificar_disponibilidad_restriccion_temporal_activa_bloquea(self):
        """Restricción TEMPORAL activa hoy SÍ debe bloquear el slot."""
        from docentes.models.docente_disponibilidad_model import Disponibilidad
        from django.utils import timezone
        from datetime import timedelta

        hoy = timezone.now().date()
        Disponibilidad.objects.create(
            docente=self.docente,
            dia_semana=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0),
            hora_fin=time(8, 0),
            disponible=False,
            tipo_restriccion='TEMPORAL',
            fecha_inicio_restriccion=hoy - timedelta(days=1),
            fecha_fin_restriccion=hoy + timedelta(days=10),
        )
        resultado = BloqueHorarioService.verificar_disponibilidad(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(6, 0), hora_fin=time(8, 0),
            docente=self.docente,
        )
        self.assertFalse(resultado['disponible'])

    def test_actualizar_bloque_exitoso(self):
        bloque = BloqueHorarioService.crear_bloque({
            'dia_semana':  BloqueHorario.DiaSemana.LUNES,
            'hora_inicio': time(6, 0), 'hora_fin': time(8, 0),
            'jornada':     BloqueHorario.Jornada.MANANA,
        })
        actualizado = BloqueHorarioService.actualizar_bloque(
            bloque, {'jornada': BloqueHorario.Jornada.TARDE}
        )
        self.assertEqual(actualizado.jornada, BloqueHorario.Jornada.TARDE)


# ─────────────────────────────────────────────────────────────────────────────
# BloqueHorario — Vistas
# ─────────────────────────────────────────────────────────────────────────────


