from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from users.models import User
from users.serializers.auth.auth_serializer import LoginSerializer, LogoutSerializer
from users.serializers.user_create_serializer import UserCreateSerializer
from users.serializers.user_self_serializer import UserSelfSerializer
from users.serializers.auth.email_verification_serializer import EmailVerificationSerializer
from users.serializers.auth.password_reset_serializer import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSelfSerializer(user, context={'request': request}).data,  # ✅ Self: incluye email_verificado
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Correo verificado correctamente.'})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = serializer.get_tokens()

        return Response({
            'user': UserSelfSerializer(user, context={'request': request}).data,  # ✅ Self: incluye email_verificado
            **tokens,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Sesión cerrada correctamente.'})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'detail': 'Si el correo existe, recibirás instrucciones para restablecer tu contraseña.'
        })


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Contraseña actualizada correctamente.'})
    
class CheckEmailExistsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        exists = User.objects.filter(email__iexact=email).exists()
        if not exists:
            raise ValidationError({'email': 'No existe una cuenta con este correo.'})
        return Response({'exists': True})