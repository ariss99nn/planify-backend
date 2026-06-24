# ficha/views/ficha/ficha_list_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from ficha.models.ficha_model import Ficha
from ficha.serializers import FichaListSerializer
from ficha.filter.ficha_filter import FichaFilter
from ficha.filter.ficha_pagination import FichaPagination
from ficha.views.ficha_base_view import FichaBaseView
from users.models.user import User


class FichaListView(FichaBaseView):
    """
    GET /api/fichas/
    - IsManager  : todas las fichas.
    - DOCENTE    : fichas donde es jefe de grupo.
    - ESTUDIANTE : solo su ficha activa.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        user = request.user
        qs = Ficha.objects.select_related(
            'version__programa', 'jefe_grupo'
        ).annotate(
            # FIX: nombre sin underscore para que FichaListSerializer
            # (IntegerField read_only sin source) acceda al valor anotado
            # en lugar de caer en la @property del modelo → N+1 queries.
            numero_estudiantes_real=Count(
                'estudiantes', filter=Q(estudiantes__activo=True)
            )
        )

        if user.rol in {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO}:
            return qs

        if user.rol == User.Rol.DOCENTE:
            if hasattr(user, 'docente'):
                return qs.filter(jefe_grupo=user.docente)
            return qs.none()

        if user.rol == User.Rol.ESTUDIANTE:
            from ficha.models.ficha_estudiante_model import FichaEstudiante
            ficha_ids = FichaEstudiante.objects.filter(
                estudiante=user,
                activo=True,
            ).values_list('ficha_id', flat=True)
            return qs.filter(pk__in=ficha_ids)

        return qs.none()

    def get(self, request):
        queryset  = self.get_queryset(request)
        filterset = FichaFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        paginator = FichaPagination()
        page      = paginator.paginate_queryset(filterset.qs, request)
        return paginator.get_paginated_response(
            FichaListSerializer(page, many=True).data
        )