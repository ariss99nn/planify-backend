from django.db import transaction
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from users.models.user import User
from users.models.email_verification import EmailVerification
from users.services.token_service import generate_numeric_code
from users.services.email_service import send_verification_email


class ResendVerificationView(APIView):
    """
    POST /api/auth/resend-verification/
    Reenvía el código de verificación de correo.
    Solo disponible si el usuario aún no ha verificado su correo.
    No revela si el email existe en el sistema.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()

        # Respuesta genérica siempre — no revelar existencia del email
        response = Response(
            {'detail': 'Si el correo existe y no está verificado, recibirás un nuevo código.'},
            status=status.HTTP_200_OK,
        )

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return response

        # Si ya está verificado no hacemos nada
        if user.email_verificado:
            return response

        with transaction.atomic():
            EmailVerification.invalidate_previous_codes(user)

            code = generate_numeric_code()
            EmailVerification.objects.create(
                user=user,
                code=code,
                expires_at=EmailVerification.get_expiration_time(),
            )

            transaction.on_commit(lambda: send_verification_email(user.email, code))

        return response