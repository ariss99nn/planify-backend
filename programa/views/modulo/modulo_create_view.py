# programa/views/modulo/modulo_create_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from programa.serializers import ModuloCreateSerializer, ModuloDetailSerializer
from programa.permissions.programa_permissions import CanManagePrograma
from programa.views.programa_base_view import ProgramaBaseView


class ModuloCreateView(ProgramaBaseView):
    permission_classes = [IsAuthenticated, CanManagePrograma]

    def post(self, request):
        serializer = ModuloCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        modulo = serializer.save()
        return Response(
            ModuloDetailSerializer(modulo).data,
            status=status.HTTP_201_CREATED,
        )