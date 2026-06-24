# bhorario/serializers/bloque_horario_create_serializer.py
from rest_framework import serializers
from bhorario.models.bloque_horario_model import BloqueHorario


class BloqueHorarioCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = BloqueHorario
        # FIX B5: se añaden es_recurrente, fecha_especifica y competencia
        fields = [
            'dia_semana', 'hora_inicio', 'hora_fin',
            'jornada', 'es_recurrente', 'fecha_especifica',
            'aula', 'docente', 'ficha', 'competencia',
        ]

    def validate(self, data):
        hora_inicio = data.get('hora_inicio')
        hora_fin    = data.get('hora_fin')
        dia         = data.get('dia_semana')
        docente     = data.get('docente')
        aula        = data.get('aula')
        ficha       = data.get('ficha')

        # Validar rango horario
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise serializers.ValidationError({
                'hora_fin': 'La hora de fin debe ser mayor a la hora de inicio.'
            })

        # Validar recurrencia vs fecha_especifica
        es_recurrente    = data.get('es_recurrente', True)
        fecha_especifica = data.get('fecha_especifica')
        if not es_recurrente and not fecha_especifica:
            raise serializers.ValidationError({
                'fecha_especifica': (
                    'Debe indicar la fecha específica si el bloque no es recurrente.'
                )
            })
        if es_recurrente and fecha_especifica:
            raise serializers.ValidationError({
                'fecha_especifica': 'Un bloque recurrente no debe tener fecha específica.'
            })

        if hora_inicio and hora_fin:
            qs_base = BloqueHorario.objects.filter(
                dia_semana=dia,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            )
            # FIX B6: se añade validación de conflicto de ficha
            if docente and qs_base.filter(docente=docente).exists():
                raise serializers.ValidationError({
                    'docente': 'El docente ya tiene un bloque asignado en ese horario.'
                })
            if aula and qs_base.filter(aula=aula).exists():
                raise serializers.ValidationError({
                    'aula': 'El aula ya tiene un bloque asignado en ese horario.'
                })
            if ficha and qs_base.filter(ficha=ficha).exists():
                raise serializers.ValidationError({
                    'ficha': 'La ficha ya tiene un bloque asignado en ese horario.'
                })

        return data