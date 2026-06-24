# ficha/serializers/ficha_estudiante/ficha_estudiante_update_serializer.py
from rest_framework import serializers
from ficha.models.ficha_estudiante_model import FichaEstudiante


class FichaEstudianteUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FichaEstudiante
        fields = ['activo', 'fecha_retiro', 'motivo_retiro']

    def validate(self, data):
        activo = data.get(
            'activo',
            self.instance.activo if self.instance else True,
        )
        fecha_retiro = data.get(
            'fecha_retiro',
            self.instance.fecha_retiro if self.instance else None,
        )
        motivo_retiro = data.get(
            'motivo_retiro',
            self.instance.motivo_retiro if self.instance else None,
        )

        if not activo:
            if not fecha_retiro:
                raise serializers.ValidationError({
                    'fecha_retiro': 'La fecha de retiro es obligatoria al desactivar.'
                })
            if not motivo_retiro:
                raise serializers.ValidationError({
                    'motivo_retiro': 'El motivo de retiro es obligatorio al desactivar.'
                })

        return data