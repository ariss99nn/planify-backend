from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models.user import User
from users.permissions import CanManageUser
from users.serializers.user_read_serializer import UserReadSerializer
from users.serializers.user_self_serializer import UserSelfSerializer
from users.serializers.user_admin_update_serializer import UserAdminUpdateSerializer
from users.serializers.actions.user_change_role_serializer import UserChangeRoleSerializer
from users.views.user.base import UserBaseView


class UserRetrieveUpdateView(UserBaseView):
    """
    GET   /api/users/{id}/     — Detalle de usuario.
    PATCH /api/users/{id}/     — Actualiza datos del usuario (admin).
    PATCH /api/users/{id}/rol/ — Cambia el rol con validación de negocio.

    Serializer de lectura diferenciado:
    - Usuario viendo su propio perfil → UserSelfSerializer (incluye email_verificado)
    - Admin/Coordinador viendo otro  → UserReadSerializer
    """

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), CanManageUser()]
        return [IsAuthenticated()]

    def _get_read_serializer(self, user, request):
        if user.pk == request.user.pk:
            return UserSelfSerializer(user, context={'request': request})
        return UserReadSerializer(user, context={'request': request})

    def _get_queryset(self, request):
        user = request.user
        if user.rol in {User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO}:
            return User.objects.all()
        if user.rol == User.Rol.DOCENTE:
            return User.objects.filter(rol=User.Rol.ESTUDIANTE)
        return User.objects.filter(pk=user.pk)

    def get(self, request, pk, action=None):
        queryset = self._get_queryset(request)
        user = queryset.filter(pk=pk).first()
        if user is None:
            from rest_framework.exceptions import NotFound
            raise NotFound('Usuario no encontrado.')

        return Response(self._get_read_serializer(user, request).data)

    def patch(self, request, pk, action=None):
        user = self.get_user_or_404(pk)
        self.check_object_permissions(request, user)

        if action == 'rol':
            serializer = UserChangeRoleSerializer(
                user,
                data=request.data,
                context={'request': request},
            )
        else:
            serializer = UserAdminUpdateSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request},
            )

        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()

        return Response(
            UserReadSerializer(updated_user, context={'request': request}).data
        )