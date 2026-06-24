# ficha/serializers/ficha_estudiante/ficha_estudiante_create_serializer.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ficha.models.ficha_model import Ficha
from ficha.models.ficha_estudiante_model import FichaEstudiante

User = get_user_model()


class FichaEstudianteCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = FichaEstudiante
        fields = ['ficha', 'estudiante', 'es_cadena']

    # ── Validadores de campo ───────────────────────────────────────────────

    def validate_estudiante(self, user):
        if user.rol != User.Rol.ESTUDIANTE:
            raise serializers.ValidationError(
                'El usuario debe tener rol ESTUDIANTE.'
            )
        if not user.estado:
            raise serializers.ValidationError(
                'No se puede asignar un estudiante inactivo.'
            )
        return user

    # ── Validador cruzado ──────────────────────────────────────────────────

    def validate(self, data):
        ficha     = data.get('ficha')
        estudiante = data.get('estudiante')
        es_cadena  = data.get('es_cadena', False)

        # FIX: validación de estado de la ficha — faltaba completamente.
        if ficha.estado != Ficha.Estado.ACTIVA:
            raise serializers.ValidationError({
                'ficha': f'La ficha {ficha.codigo_ficha} no está activa.'
            })

        # Coherencia cadena estudiante vs ficha
        if ficha.cadena_formacion and not es_cadena:
            raise serializers.ValidationError({
                'es_cadena': 'La ficha es de cadena; el estudiante debe marcarse igual.'
            })
        if not ficha.cadena_formacion and es_cadena:
            raise serializers.ValidationError({
                'es_cadena': 'La ficha no es de cadena de formación.'
            })

        # Unicidad: el estudiante no puede estar ya en esta ficha (activo o no)
        if FichaEstudiante.objects.filter(ficha=ficha, estudiante=estudiante).exists():
            raise serializers.ValidationError(
                'Este estudiante ya está asignado a esta ficha.'
            )

        # FIX: unicidad de ficha activa consistente con FichaEstudiante.clean().
        # El original solo chequeaba no-cadena; si el modelo bloqueaba cadena también,
        # el error llegaba como HTTP 500 desde save().
        activa_qs = FichaEstudiante.objects.filter(
            estudiante=estudiante, activo=True
        )
        if activa_qs.exists():
            codigo_activa = activa_qs.first().ficha.codigo_ficha
            raise serializers.ValidationError(
                f'El estudiante ya tiene una ficha activa ({codigo_activa}). '
                f'Use reasignación para cambiarlo.'
            )

        return data