from rest_framework import serializers
from users.models.user import User


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    """
    Permite a un administrador o coordinador modificar datos sensibles de un usuario:
    nombre, apellido, rol, estado activo y correo electrónico directamente
    (sin flujo de verificación por código).

    Lógica de email_verificado al cambiar email:
    - Si is_active=True  → email_verificado=True  (el admin da fe del correo)
    - Si is_active=False → email_verificado=False (el usuario deberá verificar al activarse)

    El cambio de rol con validación de negocio (mínimo un coordinador activo)
    usa UserChangeRoleSerializer del módulo actions.
    """

    class Meta:
        model = User
        fields = (
            'nombre',
            'apellido',
            'rol',
            'is_active',
            'email',
            'imagen', 
        )

    def validate_email(self, value):
        normalized = value.lower()
        qs = User.objects.filter(email__iexact=normalized)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Este correo ya está en uso.")
        return normalized

    def update(self, instance, validated_data):
        email_changed = (
            'email' in validated_data
            and validated_data['email'] != instance.email
        )

        instance = super().update(instance, validated_data)

        # Si el admin cambió el email, email_verificado sigue a is_active:
        # - is_active=True  → email_verificado=True  (el admin da fe del correo)
        # - is_active=False → email_verificado=False (el usuario deberá verificar)
        if email_changed:
            instance.email_verificado = instance.is_active
            instance.save(update_fields=['email_verificado'])

        return instance