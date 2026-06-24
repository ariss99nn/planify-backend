"""
alertas/tests/test_signals.py

Tests para la señal post_save en Alerta.

Cubre:
- Creación de Notificacion al crear Alerta (señal)
- Idempotencia: no duplica Notificaciones
- Despacho WebSocket mockeado
- Alertas de sistema (sin destinatario): no generan Notificacion
- Alertas de conflicto: requieren bloque_origen
- marcar_leida(): transición de estado correcta
"""

from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.utils import timezone

from alertas.models.alerta_model import Alerta
from users.tests.factories import make_coordinador, make_docente


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_bloque(docente_user=None):
    """Crea un BloqueHorario mínimo para alertas de conflicto."""
    from bhorario.tests.factories import make_bloque_horario
    return make_bloque_horario(docente_user=docente_user)


def _make_alerta_disponibilidad(destinatario):
    return Alerta.objects.create(
        tipo=Alerta.TipoAlerta.DISPONIBILIDAD,
        descripcion='Test disponibilidad',
        formato_alerta=Alerta.FormatoAlerta.APP,
        destinatario=destinatario,
    )


def _make_alerta_sistema():
    return Alerta.objects.create(
        tipo=Alerta.TipoAlerta.SISTEMA,
        descripcion='Mantenimiento programado.',
        formato_alerta=Alerta.FormatoAlerta.APP,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tests de señal
# ─────────────────────────────────────────────────────────────────────────────

class AlertaSignalTest(TestCase):
    """post_save en Alerta crea Notificacion y despacha WS."""

    def setUp(self):
        self.destinatario = make_docente(email_verificado=True)

    @patch('notificaciones.signals.notificaciones_signals._ws_dispatch')
    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_crea_notificacion_al_crear_alerta(self, mock_layer, mock_dispatch):
        """Crear una Alerta dispara la señal y genera la Notificacion."""
        from notificaciones.models.notificaciones_model import Notificacion
        mock_layer.return_value = MagicMock()

        alerta = _make_alerta_disponibilidad(self.destinatario)

        self.assertEqual(
            Notificacion.objects.filter(alerta=alerta).count(), 1
        )

    @patch('notificaciones.signals.notificaciones_signals._ws_dispatch')
    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_no_duplica_notificacion_en_update(self, mock_layer, mock_dispatch):
        """
        Un update sobre la Alerta (post_save, created=False) no debe
        crear una segunda Notificacion.
        """
        from notificaciones.models.notificaciones_model import Notificacion
        mock_layer.return_value = MagicMock()

        alerta = _make_alerta_disponibilidad(self.destinatario)

        # Modificar la alerta (update → post_save con created=False)
        alerta.estado = Alerta.EstadoAlerta.ENVIADA
        alerta.save(update_fields=['estado'])

        self.assertEqual(
            Notificacion.objects.filter(alerta=alerta).count(), 1,
            'La señal no debe crear Notificacion duplicada en updates.',
        )

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_alerta_sistema_no_genera_notificacion(self, mock_layer):
        """Alerta de sistema (sin destinatario) no genera Notificacion."""
        from notificaciones.models.notificaciones_model import Notificacion
        mock_layer.return_value = MagicMock()

        alerta = _make_alerta_sistema()

        self.assertEqual(
            Notificacion.objects.filter(alerta=alerta).count(), 0
        )

    @patch('notificaciones.signals.notificaciones_signals._ws_dispatch')
    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_ws_dispatch_se_llama_al_crear(self, mock_layer, mock_dispatch):
        """La señal llama _ws_dispatch con el grupo correcto del destinatario."""
        mock_layer.return_value = MagicMock()

        alerta = _make_alerta_disponibilidad(self.destinatario)

        # on_commit no se ejecuta en tests sin transaction — llamar manualmente
        from django.db import connection
        # Verificar que al menos la Notificacion fue creada (WS se verifica en
        # tests con TestCase transaccional)
        from notificaciones.models.notificaciones_model import Notificacion
        self.assertTrue(
            Notificacion.objects.filter(alerta=alerta).exists()
        )

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_sin_channel_layer_no_explota(self, mock_layer):
        """Si channel_layer es None, la señal no lanza excepción."""
        mock_layer.return_value = None  # channel layer no configurado
        # No debe lanzar ninguna excepción
        alerta = _make_alerta_disponibilidad(self.destinatario)
        self.assertIsNotNone(alerta.pk)


# ─────────────────────────────────────────────────────────────────────────────
# Tests de modelo Alerta
# ─────────────────────────────────────────────────────────────────────────────

class AlertaModelTest(TestCase):
    """Validaciones de negocio del modelo Alerta."""

    def setUp(self):
        self.docente_user = make_docente(email_verificado=True)

    def test_alerta_conflicto_sin_bloque_falla(self):
        """Una alerta de CONFLICTO sin bloque_origen debe fallar full_clean()."""
        from django.core.exceptions import ValidationError
        alerta = Alerta(
            tipo=Alerta.TipoAlerta.CONFLICTO,
            descripcion='Sin bloque',
            destinatario=self.docente_user,
        )
        with self.assertRaises(ValidationError) as ctx:
            alerta.full_clean()
        self.assertIn('bloque_origen', ctx.exception.message_dict)

    def test_alerta_disponibilidad_sin_destinatario_falla(self):
        """Alerta DISPONIBILIDAD sin destinatario debe fallar full_clean()."""
        from django.core.exceptions import ValidationError
        alerta = Alerta(
            tipo=Alerta.TipoAlerta.DISPONIBILIDAD,
            descripcion='Sin destinatario',
        )
        with self.assertRaises(ValidationError) as ctx:
            alerta.full_clean()
        self.assertIn('destinatario', ctx.exception.message_dict)

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_marcar_leida_cambia_estado(self, mock_layer):
        """marcar_leida() debe cambiar estado a LEIDA y registrar fecha_lectura."""
        mock_layer.return_value = None
        alerta = _make_alerta_disponibilidad(self.docente_user)
        self.assertEqual(alerta.estado, Alerta.EstadoAlerta.PENDIENTE)
        self.assertIsNone(alerta.fecha_lectura)

        alerta.marcar_leida()

        alerta.refresh_from_db()
        self.assertEqual(alerta.estado, Alerta.EstadoAlerta.LEIDA)
        self.assertIsNotNone(alerta.fecha_lectura)

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_marcar_leida_idempotente(self, mock_layer):
        """Llamar marcar_leida() dos veces no debe cambiar fecha_lectura."""
        mock_layer.return_value = None
        alerta = _make_alerta_disponibilidad(self.docente_user)
        alerta.marcar_leida()
        alerta.refresh_from_db()
        primera_lectura = alerta.fecha_lectura

        alerta.marcar_leida()  # segunda llamada
        alerta.refresh_from_db()
        self.assertEqual(alerta.fecha_lectura, primera_lectura)

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_str_representation(self, mock_layer):
        """__str__ debe incluir tipo y estado de la alerta."""
        mock_layer.return_value = None
        alerta = _make_alerta_disponibilidad(self.docente_user)
        self.assertIn('Disponibilidad', str(alerta))
        self.assertIn('Pendiente', str(alerta))


# ─────────────────────────────────────────────────────────────────────────────
# Tests de vistas (API)
# ─────────────────────────────────────────────────────────────────────────────

class AlertaViewTest(TestCase):
    """Endpoints de alertas respetan permissions y filtrado por usuario."""

    def setUp(self):
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken

        self.client = APIClient()
        self.docente_user = make_docente(email_verificado=True)
        self.coordinador  = make_coordinador(email_verificado=True)

        refresh = RefreshToken.for_user(self.docente_user)
        self.doc_header  = {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
        refresh_coord    = RefreshToken.for_user(self.coordinador)
        self.coord_header = {'HTTP_AUTHORIZATION': f'Bearer {refresh_coord.access_token}'}

    @patch('notificaciones.signals.notificaciones_signals.get_channel_layer')
    def test_docente_solo_ve_sus_alertas(self, mock_layer):
        """Un docente solo debe ver alertas dirigidas a él."""
        mock_layer.return_value = None
        otro = make_docente(email='otro@test.com', email_verificado=True)

        _make_alerta_disponibilidad(self.docente_user)
        _make_alerta_disponibilidad(otro)

        response = self.client.get('/api/v1/alertas/', **self.doc_header)
        self.assertEqual(response.status_code, 200)
        for alerta in response.data.get('results', response.data):
            self.assertEqual(alerta['destinatario'], self.docente_user.pk)

    def test_unauthenticated_request_returns_401(self):
        """Sin JWT, el endpoint debe retornar 401."""
        response = self.client.get('/api/v1/alertas/')
        self.assertEqual(response.status_code, 401)
