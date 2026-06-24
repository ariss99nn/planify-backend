from rest_framework import serializers
from users.models.user import User


class UserBaseSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'nombre',
            'apellido',
            'nombre_completo',
            'email',
            'rol',
            'is_active',
            'imagen_url',
            'fecha_creacion',
            'fecha_modificacion',
        )
        read_only_fields = fields

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None

    def get_nombre_completo(self, obj):
        return obj.nombre_completo