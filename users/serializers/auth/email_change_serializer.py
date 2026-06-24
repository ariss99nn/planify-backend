from django.db import transaction
from rest_framework import serializers

from users.models.user import User
from users.models.email_change import EmailChangeRequest
from users.services.token_service import generate_numeric_code
from users.services.email_service import send_email_change_email


class EmailChangeRequestSerializer(serializers.Serializer):
    """
    Solicita el cambio de correo del usuario autenticado.
    Envía un código de verificación al NUEVO correo para confirmar
    que el usuario tiene acceso a él antes de asignárselo.
    """

    new_email = serializers.EmailField()

    def validate_new_email(self, value):
        normalized = value.lower()

        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("Este correo ya está en uso.")

        if EmailChangeRequest.email_already_requested(normalized):
            raise serializers.ValidationError(
                "Ya existe una solicitud activa para este correo. Intenta en unos minutos."
            )

        return normalized

    @transaction.atomic
    def save(self, **kwargs):
        user = self.context['request'].user
        new_email = self.validated_data['new_email']

        EmailChangeRequest.invalidate_previous_requests(user)

        code = generate_numeric_code()
        EmailChangeRequest.objects.create(
            user=user,
            new_email=new_email,
            code=code,
            expires_at=EmailChangeRequest.get_expiration_time(),
        )

        # ✅ El código va al correo nuevo — verificamos acceso antes de asignarlo
        transaction.on_commit(lambda: send_email_change_email(new_email, code))


class EmailChangeConfirmSerializer(serializers.Serializer):
    """
    Confirma el cambio de correo con el código enviado al nuevo email.
    """

    code = serializers.CharField(max_length=6)

    def validate(self, data):
        user = self.context['request'].user

        try:
            req = EmailChangeRequest.objects.filter(
                user=user,
                is_used=False,
            ).latest('created_at')
        except EmailChangeRequest.DoesNotExist:
            raise serializers.ValidationError("No hay solicitud activa.")

        if not req.is_valid():
            raise serializers.ValidationError("El código ha expirado.")

        if req.code.strip() != data['code'].strip():
            raise serializers.ValidationError("Código incorrecto.")

        data['request_instance'] = req
        return data

    @transaction.atomic
    def save(self, **kwargs):
        req = self.validated_data['request_instance']
        user = req.user

        user.email = req.new_email
        user.save(update_fields=['email'])

        req.mark_as_used()

        return user