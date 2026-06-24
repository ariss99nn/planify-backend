# ficha/serializers/reasignacion/reasignacion_create_serializer.py
# FIX: imports corregidos (eliminado prefijo back.; Ficha importado desde su módulo).
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from ficha.models.ficha_model import Ficha
from ficha.models.ficha_estudiante_model import FichaEstudiante
from ficha.models.ficha_reasignacion_model import ReasignacionFicha

User = get_user_model()


class ReasignacionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ReasignacionFicha
        fields = ['estudiante', 'ficha_origen', 'ficha_destino', 'motivo']

    # ── Validadores de campo ───────────────────────────────────────────────

    def validate_estudiante(self, user):
        if user.rol != User.Rol.ESTUDIANTE:
            raise serializers.ValidationError(
                'El usuario debe tener rol ESTUDIANTE.'
            )
        return user

    # ── Validador cruzado ──────────────────────────────────────────────────

    def validate(self, data):
        estudiante    = data['estudiante']
        ficha_origen  = data['ficha_origen']
        ficha_destino = data['ficha_destino']

        if ficha_origen == ficha_destino:
            raise serializers.ValidationError(
                'La ficha de origen y destino no pueden ser la misma.'
            )

        # Verificar que el estudiante esté activo en origen
        try:
            self._relacion_origen = FichaEstudiante.objects.get(
                estudiante=estudiante,
                ficha=ficha_origen,
                activo=True,
            )
        except FichaEstudiante.DoesNotExist:
            raise serializers.ValidationError(
                f'El estudiante no está activo en la ficha {ficha_origen.codigo_ficha}.'
            )

        # Ficha destino debe estar activa
        if ficha_destino.estado != Ficha.Estado.ACTIVA:
            raise serializers.ValidationError(
                f'La ficha destino {ficha_destino.codigo_ficha} no está activa.'
            )

        # El estudiante no debe estar ya activo en destino
        if FichaEstudiante.objects.filter(
            estudiante=estudiante,
            ficha=ficha_destino,
            activo=True,
        ).exists():
            raise serializers.ValidationError(
                f'El estudiante ya está activo en la ficha destino '
                f'{ficha_destino.codigo_ficha}.'
            )

        # FIX: coherencia de cadena_formacion entre fichas.
        # Sin esta guarda, FichaEstudiante.clean() lanzaría ValidationError
        # dentro del atomic → rollback + error no controlado.
        if ficha_origen.cadena_formacion != ficha_destino.cadena_formacion:
            raise serializers.ValidationError(
                'No se puede reasignar entre fichas con distinta modalidad '
                'de cadena de formación.'
            )

        return data

    # ── Persistencia transaccional ─────────────────────────────────────────

    @transaction.atomic
    def save(self, **kwargs):
        request       = self.context.get('request')
        realizado_por = request.user if request else None
        hoy           = timezone.now().date()

        estudiante    = self.validated_data['estudiante']
        ficha_origen  = self.validated_data['ficha_origen']
        ficha_destino = self.validated_data['ficha_destino']
        motivo        = self.validated_data['motivo']

        # 1 — Desactivar en origen con motivo REASIGNADO
        self._relacion_origen.activo        = False
        self._relacion_origen.fecha_retiro  = hoy
        self._relacion_origen.motivo_retiro = FichaEstudiante.MotivoRetiro.REASIGNADO
        self._relacion_origen.save(
            update_fields=['activo', 'fecha_retiro', 'motivo_retiro']
        )

        # 2 — Crear en destino
        FichaEstudiante.objects.create(
            ficha     = ficha_destino,
            estudiante = estudiante,
            activo    = True,
            es_cadena = self._relacion_origen.es_cadena,
        )

        # 3 — Registrar reasignación
        return ReasignacionFicha.objects.create(
            estudiante    = estudiante,
            ficha_origen  = ficha_origen,
            ficha_destino = ficha_destino,
            motivo        = motivo,
            realizado_por = realizado_por,
        )