from rest_framework import serializers
from competencia.models.asignatura_model import Asignatura
from competencia.serializers.mixins import DjangoValidationErrorMixin


class AsignaturaCreateSerializer(DjangoValidationErrorMixin, serializers.ModelSerializer):

    class Meta:
        model = Asignatura
        fields = [
            'modulo', 'nombre', 'descripcion', 'tipo',
            'horas_lectivas', 'horas_practicas', 'orden', 'estado',
        ]

    def validate(self, data):
        modulo = data.get('modulo')
        orden = data.get('orden')

        if Asignatura.objects.filter(modulo=modulo, orden=orden).exists():
            raise serializers.ValidationError({
                'orden': (
                    f'Ya existe una asignatura con orden {orden} '
                    f'en el módulo "{modulo.nombre}".'
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