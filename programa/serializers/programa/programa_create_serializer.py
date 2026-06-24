# programa/serializers/programa/programa_create_serializer.py
from rest_framework import serializers
from programa.models.programa_model import Programa


class ProgramaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Programa
        fields = [
            'nombre', 'descripcion', 'nivel',
            'horas_lectivas', 'horas_practicas', 'estado',
            'trimestres_totales', 'tipo_formacion', 'trimestres_cadena',
        ]

    def validate(self, data):
        if data.get('horas_lectivas', 0) <= 0:
            raise serializers.ValidationError(
                {'horas_lectivas': 'Las horas lectivas deben ser mayores a 0.'}
            )
        if data.get('horas_practicas', 0) < 0:
            raise serializers.ValidationError(
                {'horas_practicas': 'Las horas prácticas no pueden ser negativas.'}
            )

        tipo_formacion = data.get('tipo_formacion', Programa.TipoFormacion.POR_OFERTA)
        trimestres_totales = data.get('trimestres_totales', 6)
        trimestres_cadena = data.get('trimestres_cadena')

        if tipo_formacion == Programa.TipoFormacion.CADENA_FORMACION:
            if not trimestres_cadena:
                raise serializers.ValidationError(
                    {'trimestres_cadena': 'Requerido para cadena de formación.'}
                )
            if trimestres_cadena >= trimestres_totales:
                raise serializers.ValidationError(
                    {'trimestres_cadena': 'Debe ser menor que trimestres_totales.'}
                )
        return data