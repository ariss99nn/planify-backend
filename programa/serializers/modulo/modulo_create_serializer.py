# programa/serializers/modulo/modulo_create_serializer.py
from rest_framework import serializers
from programa.models.modulo_model import Modulo


class ModuloCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Modulo
        fields = [
            'version', 'nombre', 'descripcion', 'orden',
            'horas_lectivas', 'horas_practicas', 'estado',
        ]

    def validate(self, data):
        version = data.get('version')
        orden = data.get('orden')

        if Modulo.objects.filter(version=version, orden=orden).exists():
            raise serializers.ValidationError({
                'orden': (
                    f'Ya existe un módulo con orden {orden} '
                    f'en la versión {version}.'
                )
            })
        if data.get('horas_lectivas', 0) <= 0:
            raise serializers.ValidationError(
                {'horas_lectivas': 'Las horas lectivas deben ser mayores a 0.'}
            )
        if data.get('horas_practicas', 0) < 0:
            raise serializers.ValidationError(
                {'horas_practicas': 'Las horas prácticas no pueden ser negativas.'}
            )
        return data