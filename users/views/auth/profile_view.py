from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from users.serializers.user_self_serializer import UserSelfSerializer
from users.serializers.user_profile_update_serializer import UserProfileUpdateSerializer
from users.serializers.auth.email_change_serializer import (
    EmailChangeRequestSerializer,
    EmailChangeConfirmSerializer,
)
from users.serializers.actions.user_username_change_serializer import UsernameChangeSerializer


class ProfileView(APIView):
    """
    GET  /api/auth/profile/  — Devuelve el perfil del usuario autenticado.
    PATCH /api/auth/profile/ — Actualiza nombre, apellido e imagen.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSelfSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            UserSelfSerializer(request.user, context={'request': request}).data
        )


class UsernameChangeView(APIView):
    """
    PATCH /api/auth/profile/username/
    Actualiza el nombre de usuario del usuario autenticado.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UsernameChangeSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Nombre de usuario actualizado correctamente.'},
            status=status.HTTP_200_OK,
        )


class EmailChangeRequestView(APIView):
    """
    POST /api/auth/profile/email/
    Solicita cambio de correo — envía código de verificación al nuevo email.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EmailChangeRequestSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Código de verificación enviado al nuevo correo.'},
            status=status.HTTP_200_OK,
        )


class EmailChangeConfirmView(APIView):
    """
    POST /api/auth/profile/email/confirm/
    Confirma el cambio de correo con el código recibido.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EmailChangeConfirmSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Correo actualizado correctamente.'},
            status=status.HTTP_200_OK,
        )