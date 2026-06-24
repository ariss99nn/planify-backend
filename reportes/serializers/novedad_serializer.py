# reportes/serializers/novedad_serializer.py
from rest_framework import serializers
from reportes.models.novedad_model import Novedad


class NovedadListSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(
        source='get_tipo_display', read_only=True
    )
    prioridad_display = serializers.CharField(
        source='get_prioridad_display', read_only=True
    )
    atendida_por_nombre = serializers.CharField(
        source='atendida_por.nombre_completo', read_only=True, default=None
    )
    esta_vigente = serializers.BooleanField(read_only=True)

    class Meta:
        model = Novedad
        fields = [
            'id', 'tipo', 'tipo_display',
            'prioridad', 'prioridad_display',
            'titulo', 'descripcion',
            'generada_por_sistema', 'generada_por',
            'atendida', 'atendida_por', 'atendida_por_nombre',
            'fecha_atencion', 'nota_atencion',
            'fecha_generacion', 'fecha_expiracion',
            'esta_vigente',
        ]


class NovedadCreateSerializer(serializers.ModelSerializer):
    """Solo gestión puede crear novedades manuales."""

    class Meta:
        model = Novedad
        fields = [
            'tipo', 'prioridad', 'titulo', 'descripcion',
            'fecha_expiracion',
        ]

    def validate_prioridad(self, value):
        if value not in (1, 2, 3):
            raise serializers.ValidationError('Prioridad debe ser 1 (Alta), 2 (Media) o 3 (Baja).')
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['generada_por_sistema'] = False
        if request:
            validated_data['generada_por'] = request.user
        return super().create(validated_data)


class NovedadAtenderSerializer(serializers.ModelSerializer):
    """Marcar una novedad como atendida."""

    class Meta:
        model = Novedad
        fields = ['nota_atencion']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        instance.marcar_atendida(
            usuario=request.user if request else None,
            nota=validated_data.get('nota_atencion', ''),
        )
        return instance