from django.db import transaction
from rest_framework import serializers

from users.models.user import User
from users.services.role_service import sync_user_group


class UserChangeRoleSerializer(serializers.ModelSerializer):
    """
    Cambia el rol de un usuario con validación de negocio.
    La autorización (solo COORDINADOR/ADMINISTRATIVO) se delega
    en IsManager — aquí solo se validan las reglas de negocio.
    """

    class Meta:
        model = User
        fields = ['rol']

    def validate(self, attrs):
        target = self.instance
        nuevo_rol = attrs.get('rol')

        if target.pk == self.context['request'].user.pk:
            raise serializers.ValidationError("No puede modificar su propio rol.")

        # Garantiza que siempre exista al menos un coordinador activo
        if (
            target.rol == User.Rol.COORDINADOR
            and nuevo_rol != User.Rol.COORDINADOR
        ):
            coordinadores_activos = User.objects.filter(
                rol=User.Rol.COORDINADOR,
                is_active=True,
            ).exclude(pk=target.pk).count()

            if coordinadores_activos == 0:
                raise serializers.ValidationError(
                    "Debe existir al menos un coordinador activo en el sistema."
                )

        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.rol = validated_data['rol']
        instance.save(update_fields=['rol'])
        sync_user_group(instance)
        return instance