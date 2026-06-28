from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.permissions import IsStaffLike, IsEstudiante
from .services.chatbot_service import CHRONOSIAChatbot
from .services.context_builder import ContextBuilder

_chatbot: CHRONOSIAChatbot | None = None


def _get_chatbot() -> CHRONOSIAChatbot:
    global _chatbot
    if _chatbot is None:
        _chatbot = CHRONOSIAChatbot()
    return _chatbot


class ChatRateThrottle(UserRateThrottle):
    scope = 'chat'


class IsChatbotAllowed(IsAuthenticated):
    message = 'Tu rol no tiene acceso al asistente.'

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return (
            IsStaffLike().has_permission(request, view)
            or IsEstudiante().has_permission(request, view)
        )


class ChatbotView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsChatbotAllowed]
    throttle_classes       = [ChatRateThrottle]

    def post(self, request):
        pregunta = request.data.get('pregunta', '').strip()
        historial = request.data.get('historial', [])

        if not pregunta:
            return Response(
                {'error': 'La pregunta no puede estar vacía.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(pregunta) > 1000:
            return Response(
                {'error': 'Pregunta demasiado larga (máx. 1000 caracteres).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            contexto_rol = ContextBuilder.build(request.user)
            respuesta = _get_chatbot().responder(
                pregunta=pregunta,
                historial=historial,
                contexto_rol=contexto_rol,
            )
            return Response({
                'respuesta': respuesta,
                'rol': request.user.rol,
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
