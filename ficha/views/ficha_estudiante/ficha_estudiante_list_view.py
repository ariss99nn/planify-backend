# ficha/views/ficha_estudiante/ficha_estudiante_list_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ficha.serializers import FichaEstudianteListSerializer
from ficha.filter.ficha_filter import FichaEstudianteFilter
from ficha.filter.ficha_pagination import FichaPagination
from ficha.views.ficha_base_view import FichaBaseView
from users.models.user import User

class FichaEstudianteListView(FichaBaseView):
    """
    GET /api/fichas/{id}/estudiantes/
    - IsManager: todos los estudiantes de la ficha.
    - DOCENTE: solo si es jefe de grupo.
    - ESTUDIANTE: no tiene acceso al listado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        ficha, error = self.get_ficha_or_404(pk)
        if error:
            return error

        user = request.user

        if user.rol == User.Rol.ESTUDIANTE:
            return Response(
                {'detail': 'No tienes acceso al listado de estudiantes.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.rol == User.Rol.DOCENTE:
            if not self.es_jefe_de_ficha(user, ficha):
                return Response(
                    {'detail': 'No eres jefe de grupo de esta ficha.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        queryset = ficha.estudiantes.select_related(
            'estudiante', 'ficha__version__programa'
        )
        filterset = FichaEstudianteFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)

        paginator = FichaPagination()
        page = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            FichaEstudianteListSerializer(page, many=True).data
        )