# docentes/serializers/docente_base_serializer.py
from rest_framework import serializers

class BaseDocenteSerializer(serializers.ModelSerializer):

    def validate_horas_max_semanales(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Las horas semanales deben ser mayores a 0.'
            )
        if value > 40:
            raise serializers.ValidationError(
                'El máximo regular no puede superar 40h. '
                'Para asignar más horas activa "permite_horas_extra" '
                'y define "horas_extra_autorizadas".'
            )
        return value

    def validate(self, data):
        permite = data.get(
            'permite_horas_extra',
            getattr(self.instance, 'permite_horas_extra', False) if self.instance else False,
        )
        extras = data.get(
            'horas_extra_autorizadas',
            getattr(self.instance, 'horas_extra_autorizadas', 0) if self.instance else 0,
        )
        if extras > 0 and not permite:
            raise serializers.ValidationError({
                'horas_extra_autorizadas': (
                    'No se pueden definir horas extra sin activar "permite_horas_extra".'
                )
            })
        return data