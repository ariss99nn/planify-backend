# ficha/serializers/historial_etapa/historial_etapa_list_serializer.py
# FIX: import corregido (eliminado prefijo back.).
from rest_framework import serializers
from ficha.models.ficha_historial_etapa_model import HistorialEtapa
from ficha.models.ficha_model import Ficha


class HistorialEtapaListSerializer(serializers.ModelSerializer):

    etapa_anterior_display = serializers.SerializerMethodField()
    etapa_nueva_display    = serializers.SerializerMethodField()
    cambiado_por_nombre    = serializers.CharField(
        source='cambiado_por.nombre', read_only=True, default=None
    )
    ficha_codigo = serializers.CharField(
        source='ficha.codigo_ficha', read_only=True
    )

    class Meta:
        model  = HistorialEtapa
        fields = [
            'id', 'ficha', 'ficha_codigo',
            'etapa_anterior', 'etapa_anterior_display',
            'etapa_nueva',    'etapa_nueva_display',
            'trimestre', 'fecha',
            'cambiado_por', 'cambiado_por_nombre',
        ]

    def get_etapa_anterior_display(self, obj):
        return dict(Ficha.Etapa.choices).get(obj.etapa_anterior, obj.etapa_anterior)

    def get_etapa_nueva_display(self, obj):
        return dict(Ficha.Etapa.choices).get(obj.etapa_nueva, obj.etapa_nueva)