# programa/serializers/version/version_create_serializer.py
from rest_framework import serializers
from programa.models.version_programa_model import VersionPrograma


class VersionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = VersionPrograma
        fields = [
            'programa', 'numero', 'descripcion',
            'vigente', 'fecha_inicio', 'fecha_fin',
        ]

    def validate(self, data):
        programa = data.get('programa')
        numero = data.get('numero')

        if VersionPrograma.objects.filter(
            programa=programa, numero=numero
        ).exists():
            raise serializers.ValidationError({
                'numero': (
                    f'Ya existe la versión {numero} '
                    f'para el programa "{programa.nombre}".'
                )
            })

        if data.get('fecha_fin') and data['fecha_fin'] <= data['fecha_inicio']:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })

        return data