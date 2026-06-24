# ficha/views/ficha/ficha_update_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ficha.serializers import FichaUpdateSerializer, FichaDetailSerializer
from users.permissions import IsManager
from ficha.views.ficha_base_view import FichaBaseView

class FichaUpdateView(FichaBaseView):
    """PATCH /api/fichas/{id}/update/ — solo IsManager."""
    permission_classes = [IsAuthenticated, IsManager]

    def patch(self, request, pk):
        ficha, error = self.get_ficha_or_404(pk)
        if error:
            return error
        serializer = FichaUpdateSerializer(
            ficha, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        ficha.refresh_from_db()
        return Response(FichaDetailSerializer(ficha).data)