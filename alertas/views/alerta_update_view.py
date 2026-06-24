# alertas/views/alerta_update_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from alertas.models.alerta_model import Alerta
from alertas.serializers import AlertaUpdateSerializer, AlertaListSerializer
from alertas.views.alerta_base_view import AlertaBaseView
from users.models.user import User


class AlertaUpdateView(AlertaBaseView):
    """
    PATCH /api/alertas/{id}/update/

    - Nadie (ni coordinador/administrativo) puede marcar como LEIDA una
      alerta cuyo destinatario no sea el propio usuario — fecha_lectura
      debe reflejar la lectura real del destinatario, no la de un gestor
      que solo está revisando el listado completo.
    - Coordinador/Administrativo: puede cambiar el estado de cualquier
      alerta, salvo lo anterior (LEIDA en alertas ajenas).
    - Docente/Estudiante: solo puede marcar SUS PROPIAS alertas como LEIDA;
      cualquier otro cambio de estado, o sobre alertas ajenas, se rechaza.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        alerta, error = self.get_alerta_or_404(pk)
        if error:
            return error

        user = request.user
        es_gestor = user.rol in {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO}
        nuevo_estado = request.data.get('estado')

        # Restricción universal: LEIDA solo la puede poner el destinatario.
        if (
            nuevo_estado == Alerta.EstadoAlerta.LEIDA
            and alerta.destinatario_id != user.id
        ):
            return Response(
                {'detail': 'Solo el destinatario puede marcar esta alerta como leída.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not es_gestor:
            if alerta.destinatario_id != user.id:
                return Response(
                    {'detail': 'No tienes acceso a esta alerta.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            # Usuarios no gestores solo pueden marcar como LEIDA
            if nuevo_estado and nuevo_estado != Alerta.EstadoAlerta.LEIDA:
                return Response(
                    {'detail': 'Solo puedes marcar la alerta como leída.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = AlertaUpdateSerializer(
            alerta, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(AlertaListSerializer(updated).data)