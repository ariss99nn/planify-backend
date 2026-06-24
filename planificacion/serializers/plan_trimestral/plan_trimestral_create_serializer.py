# planificacion/serializers/plan_trimestral/plan_trimestral_create_serializer.py
from rest_framework import serializers

from planificacion.models.plan_trimestral_model import PlanTrimestral


class PlanTrimestralCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = PlanTrimestral
        fields = ['ficha', 'trimestre', 'fecha_inicio', 'fecha_fin']

    def validate(self, data):
        ficha     = data.get('ficha')
        trimestre = data.get('trimestre')

        # 1. Unicidad (ficha, trimestre)
        if PlanTrimestral.objects.filter(ficha=ficha, trimestre=trimestre).exists():
            raise serializers.ValidationError(
                f'Ya existe un plan para la ficha '
                f'{ficha.codigo_ficha} en el trimestre {trimestre}.'
            )

        # 2. Trimestre dentro del rango del programa —
        #    se respeta la misma lógica que el modelo (cadena vs. total).
        programa = ficha.version.programa
        if ficha.cadena_formacion and programa.trimestres_cadena:
            trimestres_max = programa.trimestres_cadena
        else:
            trimestres_max = getattr(programa, 'trimestres_totales', None)

        if trimestres_max and trimestre > trimestres_max:
            raise serializers.ValidationError({
                'trimestre': (
                    f'El programa solo tiene {trimestres_max} trimestres.'
                )
            })

        # 3. Coherencia de fechas
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin    = data.get('fecha_fin')
        if fecha_fin and fecha_inicio and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la de inicio.'
            })

        return data