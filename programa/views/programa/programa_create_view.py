# programa/views/programa/programa_create_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from programa.serializers import ProgramaCreateSerializer, ProgramaDetailSerializer
from programa.permissions.programa_permissions import CanManagePrograma
from programa.views.programa_base_view import ProgramaBaseView


class ProgramaCreateView(ProgramaBaseView):
    """POST /api/programas/create/ — solo gestión (CanManagePrograma)."""
    permission_classes = [IsAuthenticated, CanManagePrograma]

    def post(self, request):
        serializer = ProgramaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        programa = serializer.save()
        return Response(
            ProgramaDetailSerializer(programa).data,
            status=status.HTTP_201_CREATED,
        )