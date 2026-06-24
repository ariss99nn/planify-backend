from rest_framework import serializers

from users.models.user import User


class UsernameChangeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ['username']

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError('El nombre de usuario ya está en uso.')
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data['username']
        instance.save(update_fields=['username'])
        return instance
