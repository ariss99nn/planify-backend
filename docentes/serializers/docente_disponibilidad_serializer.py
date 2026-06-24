# docentes/serializers/docente_disponibilidad_serializer.py
from rest_framework import serializers
from django.db import transaction
from docentes.models.docente_disponibilidad_model import Disponibilidad


class DisponibilidadListSerializer(serializers.ModelSerializer):
    docente_nombre = serializers.CharField(
        source='docente.nombre_completo', read_only=True
    )
    dia_display = serializers.CharField(
        source='get_dia_semana_display', read_only=True
    )
    tipo_restriccion_display = serializers.CharField(
        source='get_tipo_restriccion_display', read_only=True
    )

    class Meta:
        model = Disponibilidad
        fields = [
            'id', 'docente', 'docente_nombre',
            'dia_semana', 'dia_display',
            'hora_inicio', 'hora_fin',
            'disponible', 'motivo',
            'tipo_restriccion', 'tipo_restriccion_display',
            'fecha_inicio_restriccion', 'fecha_fin_restriccion',
        ]


class DisponibilidadCreateSerializer(serializers.ModelSerializer):
    """
    El docente puede crear su propia disponibilidad.
    El campo 'docente' se inyecta desde la vista si el usuario es DOCENTE.
    """

    class Meta:
        model = Disponibilidad
        fields = [
            'docente', 'dia_semana', 'hora_inicio', 'hora_fin',
            'disponible', 'motivo',
            'tipo_restriccion',
            'fecha_inicio_restriccion', 'fecha_fin_restriccion',
        ]

    def validate(self, data):
        disponible = data.get('disponible', True)
        motivo = data.get('motivo', '')
        if not disponible and not motivo:
            raise serializers.ValidationError({
                'motivo': 'Debe especificar un motivo si no está disponible.'
            })

        tipo = data.get('tipo_restriccion', Disponibilidad.TipoRestriccion.PERMANENTE)
        if tipo == Disponibilidad.TipoRestriccion.TEMPORAL:
            if not data.get('fecha_inicio_restriccion') or not data.get('fecha_fin_restriccion'):
                raise serializers.ValidationError({
                    'fecha_inicio_restriccion': (
                        'Las restricciones temporales requieren fecha de inicio y fin.'
                    )
                })
            if data['fecha_fin_restriccion'] <= data['fecha_inicio_restriccion']:
                raise serializers.ValidationError({
                    'fecha_fin_restriccion': 'La fecha de fin debe ser posterior a la de inicio.'
                })
        return data


class DisponibilidadUpdateSerializer(serializers.ModelSerializer):
    """
    El docente puede editar su disponibilidad.
    Gestión puede editar cualquiera.
    El campo 'docente' no es editable — usar delete + create para cambiarlo.
    """

    class Meta:
        model = Disponibilidad
        fields = [
            'dia_semana', 'hora_inicio', 'hora_fin',
            'disponible', 'motivo',
            'tipo_restriccion',
            'fecha_inicio_restriccion', 'fecha_fin_restriccion',
        ]

    def validate(self, data):
        disponible = data.get(
            'disponible',
            self.instance.disponible if self.instance else True,
        )
        motivo = data.get(
            'motivo',
            self.instance.motivo if self.instance else '',
        )
        if not disponible and not motivo:
            raise serializers.ValidationError({
                'motivo': 'Debe especificar un motivo si no está disponible.'
            })

        tipo = data.get(
            'tipo_restriccion',
            self.instance.tipo_restriccion if self.instance else Disponibilidad.TipoRestriccion.PERMANENTE,
        )
        if tipo == Disponibilidad.TipoRestriccion.TEMPORAL:
            fecha_inicio = data.get(
                'fecha_inicio_restriccion',
                self.instance.fecha_inicio_restriccion if self.instance else None,
            )
            fecha_fin = data.get(
                'fecha_fin_restriccion',
                self.instance.fecha_fin_restriccion if self.instance else None,
            )
            if not fecha_inicio or not fecha_fin:
                raise serializers.ValidationError({
                    'fecha_inicio_restriccion': (
                        'Las restricciones temporales requieren fecha de inicio y fin.'
                    )
                })
            if fecha_fin <= fecha_inicio:
                raise serializers.ValidationError({
                    'fecha_fin_restriccion': 'La fecha de fin debe ser posterior a la de inicio.'
                })
        return data