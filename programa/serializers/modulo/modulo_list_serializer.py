# programa/serializers/modulo/modulo_list_serializer.py
from rest_framework import serializers
from programa.models.modulo_model import Modulo


class ModuloListSerializer(serializers.ModelSerializer):

    version_numero = serializers.IntegerField(
        source='version.numero', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    total_horas = serializers.IntegerField(read_only=True)
    total_asignaturas = serializers.SerializerMethodField()

    class Meta:
        model = Modulo
        fields = [
            'id', 'nombre', 'orden',
            'version_numero', 'estado', 'estado_display',
            'horas_lectivas', 'horas_practicas', 'total_horas',
            'total_asignaturas',
        ]

    def get_total_asignaturas(self, obj):
        # Import local para evitar import circular (competencia.Asignatura
        # importa programa.Modulo a nivel de módulo) — mismo patrón que
        # usa VersionPrograma.total_horas para Modulo.
        from competencia.models.asignatura_model import Asignatura
        return obj.asignaturas.filter(estado=Asignatura.Estado.ACTIVA).count()