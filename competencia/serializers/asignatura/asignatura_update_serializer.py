from rest_framework import serializers
from competencia.models.asignatura_model import Asignatura
from competencia.serializers.mixins import DjangoValidationErrorMixin


class AsignaturaUpdateSerializer(DjangoValidationErrorMixin, serializers.ModelSerializer):
    """No permite cambiar el módulo al que pertenece."""

    class Meta:
        model = Asignatura
        fields = [
            'nombre', 'descripcion', 'tipo',
            'horas_lectivas', 'horas_practicas', 'orden', 'estado',
        ]

    def validate(self, data):
        orden = data.get('orden')
        if orden is not None and self.instance:
            if Asignatura.objects.filter(
                modulo=self.instance.modulo,
                orden=orden,
            ).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({
                    'orden': f'Ya existe una asignatura con orden {orden} en este módulo.'
                })

        horas_lectivas = data.get(
            'horas_lectivas',
            self.instance.horas_lectivas if self.instance else 0,
        )
        horas_practicas = data.get(
            'horas_practicas',
            self.instance.horas_practicas if self.instance else 0,
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