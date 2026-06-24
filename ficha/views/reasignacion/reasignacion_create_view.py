# ficha/views/reasignacion/reasignacion_create_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ficha.serializers import ReasignacionCreateSerializer, ReasignacionListSerializer
from users.permissions import IsManager
from ficha.views.ficha_base_view import FichaBaseView

class ReasignacionCreateView(FichaBaseView):
    """POST /api/fichas/reasignaciones/create/ — solo IsManager."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = ReasignacionCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        reasignacion = serializer.save()
        return Response(
            ReasignacionListSerializer(reasignacion).data,
            status=status.HTTP_201_CREATED,
        )