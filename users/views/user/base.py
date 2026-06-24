from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from users.models.user import User


class UserBaseView(APIView):

    def get_user_or_404(self, pk) -> User:
        """
        Retorna el usuario o lanza NotFound (HTTP 404).
        Usar en todas las vistas que reciban un pk de usuario.
        """
        user = User.objects.filter(pk=pk).first()
        if user is None:
            raise NotFound('Usuario no encontrado.')
        return user