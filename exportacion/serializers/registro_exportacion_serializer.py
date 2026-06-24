# exportacion/serializers/registro_exportacion_serializer.py
from rest_framework import serializers
from exportacion.models.exportacion_model import RegistroExportacion


class RegistroExportacionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(
        source='usuario.nombre_completo', read_only=True
    )
    tipo_display = serializers.CharField(
        source='get_tipo_display', read_only=True
    )
    formato_display = serializers.CharField(
        source='get_formato_display', read_only=True
    )

    class Meta:
        model = RegistroExportacion
        fields = [
            'id', 'usuario', 'usuario_nombre',
            'tipo', 'tipo_display',
            'formato', 'formato_display',
            'filtros', 'registros_exportados',
            'ip_origen', 'fecha',
        ]
        read_only_fields = fields