from django.test import TestCase
from channels.testing import WebsocketCommunicator
from core.asgi import application
from users.tests.factories import make_coordinador
from rest_framework_simplejwt.tokens import AccessToken


class AlertaConsumerTest(TestCase):

    async def test_conexion_sin_token_rechazada(self):
        communicator = WebsocketCommunicator(
            application, 'ws/alertas/'
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_conexion_con_token_valido(self):
        import asyncio
        from asgiref.sync import sync_to_async

        coord = await sync_to_async(make_coordinador)(
            email='coord_ws@test.com'
        )
        token = str(AccessToken.for_user(coord))
        communicator = WebsocketCommunicator(
            application, f'ws/alertas/?token={token}'
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        response = await communicator.receive_json_from()
        self.assertEqual(response['tipo'], 'conexion')
        await communicator.disconnect()