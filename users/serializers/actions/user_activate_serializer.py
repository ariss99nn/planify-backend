from rest_framework import serializers
from users.models.user import User


class UserActivateSerializer(serializers.ModelSerializer):
    """
    Activa un usuario del sistema.
    Requiere confirmación explícita para evitar activaciones accidentales.
    """

    confirmacion = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ['confirmacion']

    def validate_confirmacion(self, value):
        if value is not True:
            raise serializers.ValidationError(
                "Debe confirmar la activación del usuario."
            )
        return value

    def update(self, instance, validated_data):
        instance.is_active = True
        instance.save(update_fields=['is_active'])
        return instance