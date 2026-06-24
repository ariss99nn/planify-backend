# programa/serializers/version/version_update_serializer.py
from rest_framework import serializers
from programa.models.version_programa_model import VersionPrograma


class VersionUpdateSerializer(serializers.ModelSerializer):
    """
    No permite cambiar el programa al que pertenece la versión.
    No permite cambiar el número de versión — es el identificador.
    """

    class Meta:
        model = VersionPrograma
        fields = [
            'descripcion', 'vigente',
            'fecha_inicio', 'fecha_fin',
        ]

    def validate(self, data):
        fecha_inicio = data.get(
            'fecha_inicio',
            self.instance.fecha_inicio if self.instance else None
        )
        fecha_fin = data.get(
            'fecha_fin',
            self.instance.fecha_fin if self.instance else None
        )

        if fecha_fin and fecha_inicio and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
        return data