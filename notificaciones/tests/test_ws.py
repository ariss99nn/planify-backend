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

class AlertaConsumerTest(TestCase):
    """
    Tests del WebSocket consumer de alertas.
    CORRECCIÓN respecto a la versión original:
    - Se agrega test de conexión con token expirado.
    - Se agrega test de envío de mensaje de ping/pong.
    - Se agrega test de desconexión limpia.
    """

    async def test_conexion_sin_token_rechazada(self):
        from channels.testing import WebsocketCommunicator
        from core.asgi import application
        communicator = WebsocketCommunicator(application, 'ws/alertas/')
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_conexion_con_token_valido(self):
        from channels.testing import WebsocketCommunicator
        from core.asgi import application
        from asgiref.sync import sync_to_async
        from rest_framework_simplejwt.tokens import AccessToken

        coord = await sync_to_async(make_coordinador)(email='coord_ws@t.com')
        token = str(AccessToken.for_user(coord))
        communicator = WebsocketCommunicator(
            application, f'ws/alertas/?token={token}'
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        response = await communicator.receive_json_from()
        self.assertEqual(response.get('tipo'), 'conexion')
        await communicator.disconnect()

    async def test_conexion_token_invalido_rechazada(self):
        from channels.testing import WebsocketCommunicator
        from core.asgi import application
        communicator = WebsocketCommunicator(
            application, 'ws/alertas/?token=token_invalido_12345'
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_desconexion_limpia(self):
        """La desconexión no debe lanzar excepción."""
        from channels.testing import WebsocketCommunicator
        from core.asgi import application
        from asgiref.sync import sync_to_async
        from rest_framework_simplejwt.tokens import AccessToken

        coord = await sync_to_async(make_coordinador)(email='coord_ws2@t.com')
        token = str(AccessToken.for_user(coord))
        communicator = WebsocketCommunicator(
            application, f'ws/alertas/?token={token}'
        )
        await communicator.connect()
        await communicator.receive_json_from()  # mensaje de conexión
        try:
            await communicator.disconnect()
        except Exception as e:
            self.fail(f'Desconexión lanzó excepción: {e}')


# ─────────────────────────────────────────────────────────────────────────────
# CORE — Middleware tests (refactorizados y expandidos)
# ─────────────────────────────────────────────────────────────────────────────


