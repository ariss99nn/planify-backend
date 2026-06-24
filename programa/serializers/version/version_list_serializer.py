# programa/serializers/version/version_list_serializer.py
from rest_framework import serializers
from programa.models.version_programa_model import VersionPrograma


class VersionListSerializer(serializers.ModelSerializer):

    programa_nombre = serializers.CharField(
        source='programa.nombre', read_only=True
    )
    total_modulos = serializers.SerializerMethodField()
    total_horas = serializers.IntegerField(read_only=True)

    class Meta:
        model = VersionPrograma
        fields = [
            'id', 'numero', 'programa', 'programa_nombre',
            'vigente', 'fecha_inicio', 'fecha_fin',
            'total_modulos', 'total_horas',
        ]

    def get_total_modulos(self, obj):
        return obj.modulos.count()