# bhorario/serializers/bloque_horario_update_serializer.py
from rest_framework import serializers
from bhorario.models.bloque_horario_model import BloqueHorario


class BloqueHorarioUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = BloqueHorario
        # FIX B7: se añaden es_recurrente, fecha_especifica y competencia
        fields = [
            'dia_semana', 'hora_inicio', 'hora_fin',
            'jornada', 'es_recurrente', 'fecha_especifica',
            'aula', 'docente', 'ficha', 'competencia',
        ]

    def validate(self, data):
        instance = self.instance

        hora_inicio = data.get('hora_inicio', instance.hora_inicio if instance else None)
        hora_fin    = data.get('hora_fin',    instance.hora_fin    if instance else None)
        dia         = data.get('dia_semana',  instance.dia_semana  if instance else None)
        docente     = data.get('docente',     instance.docente     if instance else None)
        aula        = data.get('aula',        instance.aula        if instance else None)
        ficha       = data.get('ficha',       instance.ficha       if instance else None)

        es_recurrente    = data.get('es_recurrente',    instance.es_recurrente    if instance else True)
        fecha_especifica = data.get('fecha_especifica', instance.fecha_especifica if instance else None)

        # Validar rango horario
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise serializers.ValidationError({
                'hora_fin': 'La hora de fin debe ser mayor a la hora de inicio.'
            })

        # Validar recurrencia vs fecha_especifica
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
            pk      = instance.pk if instance else None
            qs_base = BloqueHorario.objects.filter(
                dia_semana=dia,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            )
            if pk:
                qs_base = qs_base.exclude(pk=pk)

            # FIX B8: se añade validación de conflicto de ficha
            if docente and qs_base.filter(docente=docente).exists():
                raise serializers.ValidationError({
                    'docente': 'El docente ya tiene un bloque en ese horario.'
                })
            if aula and qs_base.filter(aula=aula).exists():
                raise serializers.ValidationError({
                    'aula': 'El aula ya tiene un bloque en ese horario.'
                })
            if ficha and qs_base.filter(ficha=ficha).exists():
                raise serializers.ValidationError({
                    'ficha': 'La ficha ya tiene un bloque en ese horario.'
                })

        return data