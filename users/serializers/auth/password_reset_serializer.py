from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models.user import User
from users.models.password_reset import PasswordReset
from users.services.token_service import generate_numeric_code
from users.services.email_service import send_password_reset_email


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Solicita el restablecimiento de contraseña.
    No revela si el email existe en el sistema (seguridad ante enumeración).
    """

    email = serializers.EmailField()

    def save(self, **kwargs):
        email = self.validated_data['email'].lower()

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return  # No revelar existencia del email

        PasswordReset.invalidate_previous_tokens(user)

        code = generate_numeric_code()
        PasswordReset.objects.create(
            user=user,
            code=code,
            expires_at=PasswordReset.get_expiration_time(),
        )

        send_password_reset_email(user.email, code)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Confirma el restablecimiento de contraseña con el código recibido por email.
    """

    code = serializers.RegexField(r'^\d{6}$')
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    def validate(self, data):
        try:
            reset = PasswordReset.objects.get(
                code=data['code'],
                is_used=False,
            )
        except PasswordReset.DoesNotExist:
            raise ValidationError("Código inválido o expirado.")

        if not reset.is_valid():
            raise ValidationError("Código expirado.")

        data['reset_instance'] = reset
        return data

    def save(self, **kwargs):
        reset = self.validated_data['reset_instance']
        user = reset.user

        user.set_password(self.validated_data['password'])
        user.save(update_fields=['password'])

        reset.mark_as_used()

        return user