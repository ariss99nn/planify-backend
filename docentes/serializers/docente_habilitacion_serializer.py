# docentes/serializers/docente_habilitacion_serializer.py
from rest_framework import serializers
from docentes.models.docente_habilitacion_model import HabilitacionDocente


class HabilitacionDocenteListSerializer(serializers.ModelSerializer):
    docente_nombre = serializers.CharField(
        source='docente.nombre_completo', read_only=True
    )
    nivel_display = serializers.CharField(
        source='get_nivel_display', read_only=True
    )
    modulo_nombre = serializers.CharField(
        source='modulo.nombre', read_only=True, default=None
    )
    asignatura_nombre = serializers.CharField(
        source='asignatura.nombre', read_only=True, default=None
    )

    class Meta:
        model = HabilitacionDocente
        fields = [
            'id', 'docente', 'docente_nombre',
            'nivel', 'nivel_display',
            'modulo', 'modulo_nombre',
            'asignatura', 'asignatura_nombre',
            'activo', 'fecha_desde', 'fecha_hasta',
            'observaciones',
        ]


class HabilitacionDocenteCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = HabilitacionDocente
        fields = [
            'docente', 'nivel',
            'modulo', 'asignatura',
            'fecha_desde', 'fecha_hasta',
            'observaciones',
        ]

    def validate(self, data):
        nivel = data.get('nivel')
        modulo = data.get('modulo')
        asignatura = data.get('asignatura')
        docente = data.get('docente')

        if nivel == HabilitacionDocente.Nivel.MODULO:
            if not modulo:
                raise serializers.ValidationError({
                    'modulo': 'Habilitaciones de módulo requieren un módulo.'
                })
            if asignatura:
                raise serializers.ValidationError({
                    'asignatura': 'Habilitaciones de módulo no deben tener asignatura.'
                })
            # Todo registro nuevo nace activo=True (default del modelo),
            # así que esta condición siempre aplica al crear.
            if docente and modulo and HabilitacionDocente.objects.filter(
                docente=docente, modulo=modulo,
                nivel=HabilitacionDocente.Nivel.MODULO, activo=True,
            ).exists():
                raise serializers.ValidationError({
                    'modulo': 'Ya existe una habilitación activa para este docente y módulo.'
                })

        if nivel == HabilitacionDocente.Nivel.ASIGNATURA:
            if not asignatura:
                raise serializers.ValidationError({
                    'asignatura': 'Habilitaciones de asignatura requieren una asignatura.'
                })
            if modulo:
                raise serializers.ValidationError({
                    'modulo': 'Habilitaciones de asignatura no deben tener módulo.'
                })
            if docente and asignatura and HabilitacionDocente.objects.filter(
                docente=docente, asignatura=asignatura,
                nivel=HabilitacionDocente.Nivel.ASIGNATURA, activo=True,
            ).exists():
                raise serializers.ValidationError({
                    'asignatura': 'Ya existe una habilitación activa para este docente y asignatura.'
                })

        fecha_desde = data.get('fecha_desde')
        fecha_hasta = data.get('fecha_hasta')
        if fecha_hasta and fecha_desde and fecha_hasta <= fecha_desde:
            raise serializers.ValidationError({
                'fecha_hasta': 'La fecha de fin debe ser posterior a la de inicio.'
            })
        return data


class HabilitacionDocenteUpdateSerializer(serializers.ModelSerializer):
    """Solo permite cambiar activo, fecha_hasta y observaciones."""

    class Meta:
        model = HabilitacionDocente
        fields = ['activo', 'fecha_hasta', 'observaciones']

    def validate_fecha_hasta(self, value):
        if value and self.instance and value <= self.instance.fecha_desde:
            raise serializers.ValidationError(
                'La fecha de fin debe ser posterior a la fecha de inicio.'
            )
        return value

    def validate_activo(self, value):
        # Solo importa al reactivar (False -> True). Si ya estaba activo
        # o se está desactivando, no hay conflicto posible.
        instance = self.instance
        if not value or instance is None or instance.activo:
            return value

        if instance.nivel == HabilitacionDocente.Nivel.MODULO:
            conflicto = HabilitacionDocente.objects.filter(
                docente_id=instance.docente_id,
                modulo_id=instance.modulo_id,
                nivel=HabilitacionDocente.Nivel.MODULO,
                activo=True,
            ).exclude(pk=instance.pk).exists()
        else:
            conflicto = HabilitacionDocente.objects.filter(
                docente_id=instance.docente_id,
                asignatura_id=instance.asignatura_id,
                nivel=HabilitacionDocente.Nivel.ASIGNATURA,
                activo=True,
            ).exclude(pk=instance.pk).exists()

        if conflicto:
            raise serializers.ValidationError(
                'Ya existe otra habilitación activa para este docente en el mismo módulo/asignatura.'
            )
        return value