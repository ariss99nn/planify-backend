# planificacion/serializers/plan_trimestral/plan_trimestral_update_serializer.py
from rest_framework import serializers

from planificacion.models.plan_trimestral_model import PlanTrimestral


class PlanTrimestralUpdateSerializer(serializers.ModelSerializer):
    """No permite cambiar ficha ni trimestre."""

    class Meta:
        model  = PlanTrimestral
        fields = ['fecha_inicio', 'fecha_fin']

    def validate(self, data):
        fecha_inicio = data.get(
            'fecha_inicio',
            self.instance.fecha_inicio if self.instance else None,
        )
        fecha_fin = data.get('fecha_fin')
        if fecha_fin and fecha_inicio and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la de inicio.'
            })
        return data