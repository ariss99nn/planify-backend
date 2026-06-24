# ficha/views/ficha/ficha_etapa_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ficha.serializers import FichaEtapaUpdateSerializer, FichaDetailSerializer
from users.permissions import IsManager
from ficha.views.ficha_base_view import FichaBaseView


class FichaEtapaView(FichaBaseView):
    """
    PATCH /api/fichas/{id}/etapa/
    Solo IsManager. Registra historial automáticamente via señal pre_save.
    """
    permission_classes = [IsAuthenticated, IsManager]

    def patch(self, request, pk):
        ficha, error = self.get_ficha_or_404(pk)
        if error:
            return error

        serializer = FichaEtapaUpdateSerializer(
            ficha,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()  # FIX: eliminado comentario falso "← FALTA"; .save() sí estaba presente
        ficha.refresh_from_db()
        return Response(FichaDetailSerializer(ficha).data)