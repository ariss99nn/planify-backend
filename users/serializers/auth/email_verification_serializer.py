from rest_framework import serializers
from users.models.email_verification import EmailVerification


class EmailVerificationSerializer(serializers.Serializer):
    """
    Verifica el correo del usuario con el código enviado al registrarse.
    Al verificar correctamente activa la cuenta (is_active=True).
    """

    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        from users.models.user import User

        try:
            user = User.objects.get(email__iexact=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado.")

        try:
            verification = EmailVerification.objects.filter(
                user=user,
                is_used=False,
            ).latest('created_at')
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("No existe una verificación activa.")

        if verification.is_verified:
            raise serializers.ValidationError("El correo ya está verificado.")

        if not verification.is_valid():
            raise serializers.ValidationError("El código ha expirado.")

        if verification.code.strip() != data['code'].strip():
            raise serializers.ValidationError("Código incorrecto.")

        data['verification_instance'] = verification
        data['user'] = user
        return data

    def save(self, **kwargs):
        verification = self.validated_data['verification_instance']
        user = self.validated_data['user']

        verification.mark_as_verified()

        user.is_active = True
        user.email_verificado = True
        user.save(update_fields=['is_active', 'email_verificado'])

        return user