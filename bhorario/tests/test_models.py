from datetime import time
from django.test import TestCase
from django.core.exceptions import ValidationError
from bhorario.tests.factories import make_bloque
from bhorario.models.bloque_horario_model import BloqueHorario
from docentes.tests.factories import make_docente
from aulas.tests.factories import make_aula


class BloqueHorarioModelTest(TestCase):

    def test_str(self):
        bloque = make_bloque(
            hora_inicio=time(8, 0), hora_fin=time(10, 0)
        )
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

    def test_conflicto_docente(self):
        docente = make_docente(email='doc_conf@test.com')
        make_bloque(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            docente=docente,
        )
        bloque2 = BloqueHorario(
            dia_semana=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
            jornada=BloqueHorario.Jornada.MANANA,
            docente=docente,
        )
        with self.assertRaises(ValidationError):
            bloque2.clean()

    def test_conflicto_aula(self):
        aula = make_aula()
        make_bloque(
            dia=BloqueHorario.DiaSemana.MARTES,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            aula=aula,
        )
        bloque2 = BloqueHorario(
            dia_semana=BloqueHorario.DiaSemana.MARTES,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
            jornada=BloqueHorario.Jornada.MANANA,
            aula=aula,
        )
        with self.assertRaises(ValidationError):
            bloque2.clean()

    def test_mismo_docente_dias_distintos_valido(self):
        docente = make_docente(email='doc_dias@test.com')
        make_bloque(
            dia=BloqueHorario.DiaSemana.LUNES,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            docente=docente,
        )
        bloque2 = BloqueHorario(
            dia_semana=BloqueHorario.DiaSemana.MARTES,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            jornada=BloqueHorario.Jornada.MANANA,
            docente=docente,
        )
        bloque2.clean()  # no debe lanzar

    def test_ordering_por_dia_y_hora(self):
        make_bloque(dia=BloqueHorario.DiaSemana.MIERCOLES, hora_inicio=time(14, 0), hora_fin=time(16, 0))
        make_bloque(dia=BloqueHorario.DiaSemana.LUNES, hora_inicio=time(6, 0), hora_fin=time(8, 0))
        dias = list(BloqueHorario.objects.values_list('dia_semana', flat=True))
        self.assertEqual(dias, sorted(dias))