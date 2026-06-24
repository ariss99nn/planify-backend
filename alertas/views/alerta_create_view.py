# alertas/views/alerta_create_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from alertas.models.alerta_model import Alerta
from alertas.serializers import AlertaCreateSerializer, AlertaListSerializer
from alertas.views.alerta_base_view import AlertaBaseView
from alertas.permissions.alertas_permissions import CanManageAlerta
from notificaciones.signals.notificaciones_signals import dispatch_alertas_bulk
from users.models.user import User


class AlertaCreateView(AlertaBaseView):
    """
    POST /api/alertas/create/

    Modos:
      - destinatario presente   → crea 1 alerta (post_save dispara WS).
      - destinatario_rol         → crea N alertas en bulk + despacha WS manualmente.
      - ninguno (tipo=SISTEMA)    → crea 1 alerta sin destinatario.
    """
    permission_classes = [IsAuthenticated, CanManageAlerta]

    def post(self, request):
        serializer = AlertaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data       = serializer.validated_data
        rol        = data.pop('destinatario_rol', None)
        individual = data.get('destinatario')

        # Modo individual o alerta de sistema sin destinatario
        if individual or not rol:
            alerta = Alerta.objects.create(**data)
            return Response(
                AlertaListSerializer(alerta).data,
                status=status.HTTP_201_CREATED,
            )

        # Modo masivo por rol
        usuarios = User.objects.filter(rol=rol, is_active=True)
        if not usuarios.exists():
            return Response(
                {'detail': f'No hay usuarios activos con rol {rol}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        alertas = Alerta.objects.bulk_create([
            Alerta(**data, destinatario=u) for u in usuarios
        ])
        dispatch_alertas_bulk(alertas)

        return Response(
            AlertaListSerializer(alertas, many=True).data,
            status=status.HTTP_201_CREATED,
        )