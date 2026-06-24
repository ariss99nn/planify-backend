from users.serializers.user_base_serializer import UserBaseSerializer


class UserSelfSerializer(UserBaseSerializer):
    """
    Representación del usuario autenticado viendo su propio perfil.
    Expone email_verificado para que el frontend pueda mostrar alertas
    de verificación pendiente.
    """

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + (
            'email_verificado',
        )
        read_only_fields = fields