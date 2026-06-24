# ficha/serializers/ficha/ficha_update_serializer.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ficha.models.ficha_model import Ficha

User = get_user_model()


class FichaUpdateSerializer(serializers.ModelSerializer):
    """
    Actualización general de ficha.
    El cambio de etapa tiene su propio serializer (FichaEtapaUpdateSerializer)
    para garantizar que se registre el historial correctamente.
    """

    class Meta:
        model  = Ficha
        fields = [
            'jornada', 'numero_estudiantes_estimado',
            'horas_semanales_objetivo', 'trimestre',
            'estado', 'cadena_formacion',
            'jefe_grupo', 'fecha_inicio', 'fecha_finalizacion',
        ]

    # ── Validadores de campo ───────────────────────────────────────────────

    def validate_jefe_grupo(self, docente):
        if docente is None:
            return docente
        if not docente.estado:
            raise serializers.ValidationError(
                'El jefe de grupo no puede ser un docente inactivo.'
            )
        return docente

    def validate_numero_estudiantes_estimado(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'El número de estudiantes estimado debe ser mayor a 0.'
            )
        return value

    def validate_horas_semanales_objetivo(self, value):
        # FIX: validación faltante — espejo de FichaCreateSerializer.
        if value <= 0:
            raise serializers.ValidationError(
                'Las horas semanales objetivo deben ser mayor a 0.'
            )
        return value

    # ── Validador cruzado ──────────────────────────────────────────────────

    def validate(self, data):
        # Fechas
        fecha_inicio = data.get(
            'fecha_inicio',
            self.instance.fecha_inicio if self.instance else None,
        )
        fecha_fin = data.get('fecha_finalizacion')
        if fecha_fin and fecha_inicio and fecha_fin < fecha_inicio:
            raise serializers.ValidationError({
                'fecha_finalizacion': 'No puede ser anterior a fecha_inicio.'
            })

        # FIX: trimestre vs tope del programa.
        # Necesario porque el modelo lo valida en clean() pero DRF no captura
        # ese ValidationError si viene de save() → HTTP 500 sin esto.
        if self.instance and 'trimestre' in data:
            trimestre = data['trimestre']
            if trimestre < 1:
                raise serializers.ValidationError({
                    'trimestre': 'El trimestre debe ser al menos 1.'
                })
            cadena   = data.get('cadena_formacion', self.instance.cadena_formacion)
            programa = self.instance.version.programa
            tope = (
                programa.trimestres_cadena
                if (cadena and programa.trimestres_cadena)
                else programa.trimestres_totales
            )
            if tope and trimestre > tope:
                raise serializers.ValidationError({
                    'trimestre': f'No puede superar {tope} para este programa.'
                })

        # Cambio de cadena_formacion con estudiantes activos
        if self.instance and 'cadena_formacion' in data:
            if data['cadena_formacion'] != self.instance.cadena_formacion:
                if self.instance.estudiantes.filter(activo=True).exists():
                    raise serializers.ValidationError({
                        'cadena_formacion': (
                            'No se puede cambiar el tipo de formación '
                            'con estudiantes activos.'
                        )
                    })

        return data