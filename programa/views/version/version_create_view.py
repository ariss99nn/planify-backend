# programa/views/version/version_create_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from programa.serializers import VersionCreateSerializer, VersionDetailSerializer
from programa.permissions.programa_permissions import CanManagePrograma
from programa.views.programa_base_view import ProgramaBaseView


class VersionCreateView(ProgramaBaseView):
    permission_classes = [IsAuthenticated, CanManagePrograma]

    def post(self, request):
        serializer = VersionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        version = serializer.save()
        return Response(
            VersionDetailSerializer(version).data,
            status=status.HTTP_201_CREATED,
        )