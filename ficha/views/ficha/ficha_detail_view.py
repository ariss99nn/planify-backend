# ficha/views/ficha/ficha_detail_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ficha.serializers import FichaDetailSerializer
from ficha.views.ficha_base_view import FichaBaseView
from users.models.user import User


class FichaDetailView(FichaBaseView):
    """
    GET /api/fichas/{id}/
    - IsManager : cualquier ficha.
    - DOCENTE   : solo si es jefe de grupo.
    - ESTUDIANTE: solo si está activo en esa ficha.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # FIX: pre-cargar historial_etapas para que get_historial_etapas_reciente
        # del serializer no ejecute una query extra por request.
        ficha, error = self.get_ficha_or_404(pk, prefetch=['historial_etapas'])
        if error:
            return error

        user = request.user

        if user.rol == User.Rol.DOCENTE:
            if not self.es_jefe_de_ficha(user, ficha):
                return Response(
                    {'detail': 'No eres jefe de grupo de esta ficha.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if user.rol == User.Rol.ESTUDIANTE:
            from ficha.models.ficha_estudiante_model import FichaEstudiante
            if not FichaEstudiante.objects.filter(
                ficha=ficha, estudiante=user, activo=True
            ).exists():
                return Response(
                    {'detail': 'No tienes acceso a esta ficha.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(FichaDetailSerializer(ficha).data)