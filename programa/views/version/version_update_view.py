# programa/views/version/version_update_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from programa.serializers import VersionUpdateSerializer, VersionDetailSerializer
from programa.permissions.programa_permissions import CanManagePrograma
from programa.views.programa_base_view import ProgramaBaseView


class VersionUpdateView(ProgramaBaseView):
    permission_classes = [IsAuthenticated, CanManagePrograma]

    def patch(self, request, pk):
        version, error = self.get_version_or_404(pk)
        if error:
            return error
        serializer = VersionUpdateSerializer(
            version, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(VersionDetailSerializer(version).data)