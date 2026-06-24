from rest_framework import serializers
from users.models.user import User


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Permite al usuario autenticado actualizar su perfil básico.
    Excluye intencionalmente: rol, is_active, email, contraseña, email_verificado.
    El cambio de email tiene su propio flujo con verificación (email_change_serializer).
    """

    class Meta:
        model = User
        fields = (
            'nombre',
            'apellido',
            'imagen',
        )