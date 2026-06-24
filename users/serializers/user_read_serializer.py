from users.serializers.user_base_serializer import UserBaseSerializer


class UserReadSerializer(UserBaseSerializer):
    """
    Representación de usuario para listados y detalle general.
    Usado por admins y coordinadores al gestionar usuarios.
    """
    pass