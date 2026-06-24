from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import CanManageUser
from users.serializers.actions.user_activate_serializer import UserActivateSerializer
from users.views.user.base import UserBaseView


class UserActivateView(UserBaseView):
    """
    PATCH /api/users/{id}/activate/
    Solo COORDINADOR y ADMINISTRATIVO con CanManageUser.
    """
    permission_classes = [IsAuthenticated, CanManageUser]

    def patch(self, request, pk):
        user = self.get_user_or_404(pk)
        self.check_object_permissions(request, user)

        serializer = UserActivateSerializer(
            user,
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'detail': 'Usuario activado correctamente.'})