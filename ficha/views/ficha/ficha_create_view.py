# ficha/views/ficha/ficha_create_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ficha.serializers import FichaCreateSerializer, FichaDetailSerializer
from users.permissions import IsManager
from ficha.views.ficha_base_view import FichaBaseView

class FichaCreateView(FichaBaseView):
    """POST /api/fichas/create/ — solo IsManager."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = FichaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ficha = serializer.save()
        return Response(
            FichaDetailSerializer(ficha).data,
            status=status.HTTP_201_CREATED,
        )