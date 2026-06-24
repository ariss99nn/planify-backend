# ficha/serializers/ficha/ficha_etapa_update_serializer.py
from rest_framework import serializers
from ficha.models.ficha_model import Ficha


class FichaEtapaUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer exclusivo para cambiar la etapa de una ficha.
    Inyecta _cambiado_por en la instancia para que la señal
    pre_save registre quién hizo el cambio en HistorialEtapa.
    """

    class Meta:
        model  = Ficha
        fields = ['etapa', 'trimestre']

    # FIX: eliminado validate_etapa — DRF valida choices automáticamente en
    # ModelSerializer; el método era letra muerta y generaba ruido.

    def validate(self, data):
        # No permitir revertir PRODUCTIVA → LECTIVA
        if self.instance and 'etapa' in data:
            etapa_actual = self.instance.etapa
            etapa_nueva  = data['etapa']
            if (
                etapa_actual == Ficha.Etapa.PRODUCTIVA
                and etapa_nueva  == Ficha.Etapa.LECTIVA
            ):
                raise serializers.ValidationError({
                    'etapa': 'No se puede revertir de Productiva a Lectiva.'
                })

        # FIX: trimestre vs tope del programa (mismo problema que FichaUpdateSerializer).
        if self.instance and 'trimestre' in data:
            trimestre = data['trimestre']
            if trimestre < 1:
                raise serializers.ValidationError({
                    'trimestre': 'El trimestre debe ser al menos 1.'
                })
            programa = self.instance.version.programa
            cadena   = self.instance.cadena_formacion
            tope = (
                programa.trimestres_cadena
                if (cadena and programa.trimestres_cadena)
                else programa.trimestres_totales
            )
            if tope and trimestre > tope:
                raise serializers.ValidationError({
                    'trimestre': f'No puede superar {tope} para este programa.'
                })

        return data

    def save(self, **kwargs):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.instance._cambiado_por = request.user
        return super().save(**kwargs)