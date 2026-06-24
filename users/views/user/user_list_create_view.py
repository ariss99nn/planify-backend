from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models.user import User
from users.filters.user_filter import UserFilter, UserPagination
from users.permissions import IsManager
from users.serializers.user_read_serializer import UserReadSerializer
from users.serializers.user_create_serializer import UserCreateSerializer
from users.views.user.base import UserBaseView


class UserListCreateView(UserBaseView):
    """
    GET  /api/v1/users/ — Lista usuarios según rol del solicitante.
    POST /api/v1/users/ — Crea un usuario. Solo COORDINADOR y ADMINISTRATIVO.
    """

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]

    def get(self, request):
        user = request.user

        if user.rol in {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO}:
            queryset = User.objects.select_related('docente').all()
        elif user.rol == User.Rol.DOCENTE:
            queryset = User.objects.select_related('docente').filter(rol=User.Rol.ESTUDIANTE)
        else:
            queryset = User.objects.none()

        filterset = UserFilter(request.GET, queryset=queryset, request=request)
        queryset  = filterset.qs

        paginator = UserPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = UserReadSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        serializer = UserReadSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        self.check_permissions(request)
        serializer = UserCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserReadSerializer(user, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
