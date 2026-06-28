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

class AlertaSignalTest(TestCase):

    def setUp(self):
        self.destinatario = make_user_docente(email='dest_alerta@test.com')

    def _make_alerta(self):
        from alertas.models.alerta_model import Alerta
        return Alerta.objects.create(
            tipo=Alerta.TipoAlerta.DISPONIBILIDAD,
            descripcion='Test',
            formato_alerta=Alerta.FormatoAlerta.APP,
            destinatario=self.destinatario,
        )

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_crear_alerta_crea_notificacion(self, mock_layer):
        from notificaciones.models.notificaciones_model import Notificacion
        mock_layer.return_value = MagicMock()
        alerta = self._make_alerta()
        self.assertEqual(
            Notificacion.objects.filter(alerta=alerta).count(), 1
        )

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_update_alerta_no_duplica_notificacion(self, mock_layer):
        from alertas.models.alerta_model import Alerta
        from notificaciones.models.notificaciones_model import Notificacion
        mock_layer.return_value = MagicMock()
        alerta = self._make_alerta()
        alerta.estado = Alerta.EstadoAlerta.ENVIADA
        alerta.save(update_fields=['estado'])
        self.assertEqual(
            Notificacion.objects.filter(alerta=alerta).count(), 1
        )

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_alerta_sistema_no_genera_notificacion(self, mock_layer):
        from alertas.models.alerta_model import Alerta
        from notificaciones.models.notificaciones_model import Notificacion
        mock_layer.return_value = MagicMock()
        alerta = Alerta.objects.create(
            tipo=Alerta.TipoAlerta.SISTEMA,
            descripcion='Mantenimiento',
            formato_alerta=Alerta.FormatoAlerta.APP,
        )
        self.assertEqual(
            Notificacion.objects.filter(alerta=alerta).count(), 0
        )

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_sin_channel_layer_no_explota(self, mock_layer):
        mock_layer.return_value = None
        alerta = self._make_alerta()
        self.assertIsNotNone(alerta.pk)



class AlertaModelTest(TestCase):

    def setUp(self):
        self.docente_user = make_user_docente(email='doc_alm@test.com')

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_marcar_leida_cambia_estado(self, mock_layer):
        from alertas.models.alerta_model import Alerta
        mock_layer.return_value = None
        alerta = Alerta.objects.create(
            tipo=Alerta.TipoAlerta.DISPONIBILIDAD,
            descripcion='Leer',
            destinatario=self.docente_user,
        )
        self.assertEqual(alerta.estado, Alerta.EstadoAlerta.PENDIENTE)
        alerta.marcar_leida()
        alerta.refresh_from_db()
        self.assertEqual(alerta.estado, Alerta.EstadoAlerta.LEIDA)
        self.assertIsNotNone(alerta.fecha_lectura)

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_marcar_leida_idempotente(self, mock_layer):
        from alertas.models.alerta_model import Alerta
        mock_layer.return_value = None
        alerta = Alerta.objects.create(
            tipo=Alerta.TipoAlerta.DISPONIBILIDAD,
            descripcion='Doble lectura',
            destinatario=self.docente_user,
        )
        alerta.marcar_leida()
        alerta.refresh_from_db()
        primera = alerta.fecha_lectura
        alerta.marcar_leida()
        alerta.refresh_from_db()
        self.assertEqual(alerta.fecha_lectura, primera)

    def test_alerta_conflicto_sin_bloque_falla(self):
        from alertas.models.alerta_model import Alerta
        alerta = Alerta(
            tipo=Alerta.TipoAlerta.CONFLICTO,
            descripcion='Sin bloque',
            destinatario=self.docente_user,
        )
        with self.assertRaises(ValidationError) as ctx:
            alerta.full_clean()
        self.assertIn('bloque_origen', ctx.exception.message_dict)

    def test_alerta_disponibilidad_sin_destinatario_falla(self):
        from alertas.models.alerta_model import Alerta
        alerta = Alerta(
            tipo=Alerta.TipoAlerta.DISPONIBILIDAD,
            descripcion='Sin destinatario',
        )
        with self.assertRaises(ValidationError) as ctx:
            alerta.full_clean()
        self.assertIn('destinatario', ctx.exception.message_dict)



class AlertaViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_av@test.com')
        self.docente_user = make_user_docente(email='doc_av@test.com')
        self.estudiante = make_estudiante(email='est_av@test.com')

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_docente_solo_ve_sus_alertas(self, mock_layer):
        from alertas.models.alerta_model import Alerta
        mock_layer.return_value = None
        otro = make_user_docente(email='otro_av@test.com')
        Alerta.objects.create(
            tipo=Alerta.TipoAlerta.SISTEMA,
            descripcion='Para docente',
            destinatario=self.docente_user,
        )
        Alerta.objects.create(
            tipo=Alerta.TipoAlerta.SISTEMA,
            descripcion='Para otro',
            destinatario=otro,
        )
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.get(f'{BASE}/alertas/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)

    def test_sin_autenticacion_retorna_401(self):
        r = self.client.get(f'{BASE}/alertas/')
        self.assertEqual(r.status_code, 401)

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_docente_marca_su_alerta_leida(self, mock_layer):
        from alertas.models.alerta_model import Alerta
        mock_layer.return_value = None
        alerta = Alerta.objects.create(
            tipo=Alerta.TipoAlerta.SISTEMA,
            descripcion='Leer esto',
            destinatario=self.docente_user,
        )
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.patch(
            f'{BASE}/alertas/{alerta.pk}/update/',
            {'estado': Alerta.EstadoAlerta.LEIDA},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 200)
        alerta.refresh_from_db()
        self.assertEqual(alerta.estado, Alerta.EstadoAlerta.LEIDA)

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_docente_no_puede_actualizar_alerta_ajena(self, mock_layer):
        from alertas.models.alerta_model import Alerta
        mock_layer.return_value = None
        alerta = Alerta.objects.create(
            tipo=Alerta.TipoAlerta.SISTEMA,
            descripcion='Ajena',
            destinatario=self.estudiante,
        )
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.patch(
            f'{BASE}/alertas/{alerta.pk}/update/',
            {'estado': Alerta.EstadoAlerta.LEIDA},
            format='json', **headers,
        )
        self.assertEqual(r.status_code, 403)


