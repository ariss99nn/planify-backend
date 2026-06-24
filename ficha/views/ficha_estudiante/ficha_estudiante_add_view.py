# ficha/views/ficha_estudiante/ficha_estudiante_add_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ficha.serializers import (
    FichaEstudianteCreateSerializer,
    FichaEstudianteListSerializer,
)
from users.permissions import IsManager
from ficha.views.ficha_base_view import FichaBaseView

class FichaEstudianteAddView(FichaBaseView):
    """POST /api/fichas/{id}/estudiantes/add/ — solo IsManager."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request, pk):
        ficha, error = self.get_ficha_or_404(pk)
        if error:
            return error

        data = {**request.data, 'ficha': ficha.pk}
        serializer = FichaEstudianteCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        relacion = serializer.save()
        return Response(
            FichaEstudianteListSerializer(relacion).data,
            status=status.HTTP_201_CREATED,
        )