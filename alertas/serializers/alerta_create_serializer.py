# alertas/serializers/alerta_create_serializer.py
from rest_framework import serializers
from alertas.models.alerta_model import Alerta
from users.models.user import User


class AlertaCreateSerializer(serializers.ModelSerializer):
    """
    Campos de creación manual por admin/coordinador.

    Modos mutuamente excluyentes:
      - destinatario      → alerta individual
      - destinatario_rol  → alerta para todos los usuarios activos de ese rol
      - ninguno (solo con tipo=SISTEMA) → alerta de sistema sin destinatario

    Si se envían destinatario y destinatario_rol, destinatario tiene prioridad.

    La creación real (incluyendo el modo bulk) la maneja AlertaCreateView;
    este serializer solo valida — create() no se utiliza.
    """
    destinatario_rol = serializers.ChoiceField(
        choices=User.Rol.choices,
        required=False,
        write_only=True,
        help_text='Enviar a todos los usuarios activos de este rol.',
    )

    class Meta:
        model  = Alerta
        fields = [
            'tipo', 'descripcion', 'formato_alerta',
            'bloque_origen', 'destinatario', 'destinatario_rol',
        ]

    def validate(self, data):
        tipo = data.get('tipo')
        destinatario = data.get('destinatario')
        destinatario_rol = data.get('destinatario_rol')

        if (
            tipo == Alerta.TipoAlerta.CONFLICTO
            and not data.get('bloque_origen')
        ):
            raise serializers.ValidationError(
                {'bloque_origen': 'Las alertas de conflicto requieren un bloque origen.'}
            )
        if tipo != Alerta.TipoAlerta.SISTEMA and not destinatario and not destinatario_rol:
            raise serializers.ValidationError(
                {'destinatario': 'Obligatorio para alertas que no son de sistema.'}
            )
        return data