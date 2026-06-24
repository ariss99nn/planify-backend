from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import CanManageUser
from users.serializers.actions.user_desactivate_serializer import UserDesactivateSerializer
from users.views.user.base import UserBaseView


class UserDesactivateView(UserBaseView):
    """
    PATCH /api/users/{id}/desactivar/
    Solo COORDINADOR y ADMINISTRATIVO con CanManageUser.
    Nadie puede desactivarse a sí mismo.
    """
    permission_classes = [IsAuthenticated, CanManageUser]

    def patch(self, request, pk):
        user = self.get_user_or_404(pk)           # ✅ lanza NotFound directamente

        self.check_object_permissions(request, user)

        serializer = UserDesactivateSerializer(
            user,
            data=request.data,
            context={'request': request},          # ✅ context añadido
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'detail': 'Usuario desactivado correctamente.'})