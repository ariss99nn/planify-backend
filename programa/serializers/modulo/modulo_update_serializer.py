# programa/serializers/modulo/modulo_update_serializer.py
from rest_framework import serializers
from programa.models.modulo_model import Modulo


class ModuloUpdateSerializer(serializers.ModelSerializer):
    """
    No permite cambiar la versión a la que pertenece el módulo.
    """

    class Meta:
        model = Modulo
        fields = [
            'nombre', 'descripcion', 'orden',
            'horas_lectivas', 'horas_practicas', 'estado',
        ]

    def validate(self, data):
        orden = data.get('orden')
        if orden is not None and self.instance:
            if Modulo.objects.filter(
                version=self.instance.version,
                orden=orden,
            ).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({
                    'orden': f'Ya existe un módulo con orden {orden} en esta versión.'
                })

        horas_lectivas = data.get(
            'horas_lectivas', self.instance.horas_lectivas if self.instance else 0
        )
        horas_practicas = data.get(
            'horas_practicas', self.instance.horas_practicas if self.instance else 0
        )
        if horas_lectivas <= 0:
            raise serializers.ValidationError(
                {'horas_lectivas': 'Las horas lectivas deben ser mayores a 0.'}
            )
        if horas_practicas < 0:
            raise serializers.ValidationError(
                {'horas_practicas': 'Las horas prácticas no pueden ser negativas.'}
            )
        return data