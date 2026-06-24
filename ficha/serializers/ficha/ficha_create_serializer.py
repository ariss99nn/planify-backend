# ficha/serializers/ficha/ficha_create_serializer.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ficha.models.ficha_model import Ficha

User = get_user_model()


class FichaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Ficha
        fields = [
            'codigo_ficha', 'version', 'jornada',
            'numero_estudiantes_estimado', 'etapa',
            'horas_semanales_objetivo', 'trimestre',
            'estado', 'cadena_formacion',
            'jefe_grupo', 'fecha_inicio', 'fecha_finalizacion',
        ]

    # ── Validadores de campo ───────────────────────────────────────────────

    def validate_jefe_grupo(self, docente):
        if docente is None:
            return docente
        if not docente.estado:
            raise serializers.ValidationError(
                'El jefe de grupo no puede ser un docente inactivo.'
            )
        return docente

    def validate_numero_estudiantes_estimado(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'El número de estudiantes estimado debe ser mayor a 0.'
            )
        return value

    def validate_horas_semanales_objetivo(self, value):
        # FIX: validación faltante — modelo usa PositiveIntegerField que permite 0.
        if value <= 0:
            raise serializers.ValidationError(
                'Las horas semanales objetivo deben ser mayor a 0.'
            )
        return value

    def validate_trimestre(self, value):
        # FIX: validación faltante — PositiveIntegerField permite 0.
        if value < 1:
            raise serializers.ValidationError(
                'El trimestre debe ser al menos 1.'
            )
        return value

    # ── Validador cruzado ──────────────────────────────────────────────────

    def validate(self, data):
        version  = data.get('version')
        cadena   = data.get('cadena_formacion', False)
        trimestre = data.get('trimestre')

        # Fechas
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin    = data.get('fecha_finalizacion')
        if fecha_fin and fecha_inicio and fecha_fin < fecha_inicio:
            raise serializers.ValidationError({
                'fecha_finalizacion': 'No puede ser anterior a fecha_inicio.'
            })

        # Versión vigente
        if version and not version.vigente:
            raise serializers.ValidationError({
                'version': 'Solo se pueden crear fichas sobre versiones vigentes.'
            })

        if version:
            programa = version.programa

            # Cadena coherente con el programa
            if cadena and programa.trimestres_cadena is None:
                raise serializers.ValidationError({
                    'cadena_formacion': 'El programa no tiene configurados trimestres para cadena.'
                })

            # FIX: trimestre vs tope del programa.
            # Sin esto, el modelo lanza ValidationError en save() que DRF no captura → HTTP 500.
            if trimestre is not None:
                tope = (
                    programa.trimestres_cadena
                    if (cadena and programa.trimestres_cadena)
                    else programa.trimestres_totales
                )
                if tope and trimestre > tope:
                    raise serializers.ValidationError({
                        'trimestre': f'No puede superar {tope} para este programa.'
                    })

        return data