# notificaciones/views/notificacion_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from notificaciones.models import Notificacion
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)


class NotificacionListView(APIView):
    """
    GET /api/notificaciones/
    Gestión ve todas. Docente y estudiante ven solo las suyas.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = Notificacion.objects.select_related(
            'alerta', 'destinatario'
        ).order_by('-fecha_creacion')

        if user.rol not in ROLES_GESTION:
            qs = qs.filter(destinatario=user)

        estado = request.query_params.get('estado')
        canal = request.query_params.get('canal')
        if estado:
            qs = qs.filter(estado=estado)
        if canal:
            qs = qs.filter(canal=canal)

        data = [
            {
                'id': n.pk,
                'alerta_id': n.alerta_id,
                'canal': n.canal,
                'estado': n.estado,
                'intentos': n.intentos,
                'fecha_creacion': n.fecha_creacion,
                'fecha_envio': n.fecha_envio,
            }
            for n in qs
        ]
        return Response(data)