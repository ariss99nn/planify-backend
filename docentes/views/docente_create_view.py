# docentes/views/docente_create_view.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from docentes.permissions.docente_permissions import CanManageDocente
from docentes.serializers.docente_create_serializer import DocenteCreateSerializer
from docentes.serializers.docente_detail_serializer import DocenteDetailSerializer
from docentes.views.docente_base_view import DocenteBaseView

class DocenteCreateView(DocenteBaseView):
    permission_classes = [IsAuthenticated, CanManageDocente]

    def post(self, request):
        serializer = DocenteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        docente = serializer.save()
        return Response(
            DocenteDetailSerializer(docente).data,
            status=status.HTTP_201_CREATED,
        )