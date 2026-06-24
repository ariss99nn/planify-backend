# docentes/views/docente_disponibilidad_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from docentes.models.docente_disponibilidad_model import Disponibilidad
from docentes.serializers.docente_disponibilidad_serializer import (
    DisponibilidadListSerializer,
    DisponibilidadCreateSerializer,
    DisponibilidadUpdateSerializer,
)
from docentes.permissions.docente_permissions import CanManageDisponibilidad
from docentes.views.docente_base_view import DocenteBaseView
from users.models.user import User

ROLES_GESTION = (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO)

def _puede_acceder_docente(request, docente):
    """
    Gestión: accede a cualquier docente.
    Docente: solo accede a sí mismo.
    """
    if request.user.rol in ROLES_GESTION:
        return True
    return (
        request.user.rol == User.Rol.DOCENTE
        and hasattr(request.user, 'docente')
        and request.user.docente == docente
    )


class DisponibilidadListCreateView(DocenteBaseView):
    """
    GET  /api/docentes/{pk}/disponibilidad/  → lista las disponibilidades.
    POST /api/docentes/{pk}/disponibilidad/  → crea una nueva disponibilidad.

    Gestión ve y crea para cualquier docente.
    Docente solo ve y crea la suya.
    """
    permission_classes = [IsAuthenticated, CanManageDisponibilidad]

    def get(self, request, pk):
        docente, error = self.get_docente_or_404(pk)
        if error:
            return error

        if not _puede_acceder_docente(request, docente):
            return Response(
                {'detail': 'No tienes permiso para ver la disponibilidad de este docente.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        qs = (
            Disponibilidad.objects
            .filter(docente=docente)
            .order_by('dia_semana', 'hora_inicio')
        )
        return Response(DisponibilidadListSerializer(qs, many=True).data)

    def post(self, request, pk):
        docente, error = self.get_docente_or_404(pk)
        if error:
            return error

        if not _puede_acceder_docente(request, docente):
            return Response(
                {'detail': 'Solo puedes crear tu propia disponibilidad.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        data['docente'] = docente.pk

        serializer = DisponibilidadCreateSerializer(
            data=data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        disponibilidad = serializer.save()

        # Notificar a gestión cuando el docente registra no disponibilidad
        if not disponibilidad.disponible:
            from docentes.services.docente_disponibilidad_service import (
                procesar_cambio_disponibilidad,
            )
            procesar_cambio_disponibilidad(disponibilidad, request.user)

        return Response(
            DisponibilidadListSerializer(disponibilidad).data,
            status=status.HTTP_201_CREATED,
        )


class DisponibilidadDetailView(DocenteBaseView):
    """
    PATCH  /api/docentes/{pk}/disponibilidad/{disp_pk}/  → edita.
    DELETE /api/docentes/{pk}/disponibilidad/{disp_pk}/  → elimina (solo gestión).

    Docente puede editar la suya pero NO eliminar (trazabilidad).
    """
    permission_classes = [IsAuthenticated, CanManageDisponibilidad]

    def _get_disponibilidad(self, docente, disp_pk):
        try:
            return Disponibilidad.objects.select_related('docente__user').get(
                pk=disp_pk, docente=docente
            )
        except Disponibilidad.DoesNotExist:
            return None

    def patch(self, request, pk, disp_pk):
        docente, error = self.get_docente_or_404(pk)
        if error:
            return error

        disponibilidad = self._get_disponibilidad(docente, disp_pk)
        if disponibilidad is None:
            return Response(
                {'detail': 'Disponibilidad no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # has_object_permission recibe la instancia de Disponibilidad → correcto
        self.check_object_permissions(request, disponibilidad)

        disponible_antes = disponibilidad.disponible

        serializer = DisponibilidadUpdateSerializer(
            disponibilidad,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        actualizada = serializer.save()

        # Notificar si el docente cambió su estado a no disponible
        if disponible_antes and not actualizada.disponible:
            from docentes.services.docente_disponibilidad_service import (
                procesar_cambio_disponibilidad,
            )
            procesar_cambio_disponibilidad(actualizada, request.user)

        return Response(DisponibilidadListSerializer(actualizada).data)

    def delete(self, request, pk, disp_pk):
        docente, error = self.get_docente_or_404(pk)
        if error:
            return error

        disponibilidad = self._get_disponibilidad(docente, disp_pk)
        if disponibilidad is None:
            return Response(
                {'detail': 'Disponibilidad no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # El permiso ya bloquea DELETE para docentes; gestión siempre pasa
        self.check_object_permissions(request, disponibilidad)

        disponibilidad.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)