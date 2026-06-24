from users.views.auth import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    CheckEmailExistsView,
    ProfileView,
    EmailChangeRequestView,
    EmailChangeConfirmView,
)
from users.views.user import (
    UserListCreateView,
    UserRetrieveUpdateView,
    UserDesactivateView,
    UserActivateView,
)

__all__ = [
    # auth
    'RegisterView',
    'VerifyEmailView',
    'LoginView',
    'LogoutView',
    'PasswordResetRequestView',
    'PasswordResetConfirmView',
    'CheckEmailExistsView',
    # perfil propio
    'ProfileView',
    'EmailChangeRequestView',
    'EmailChangeConfirmView',
    # gestión de usuarios
    'UserListCreateView',
    'UserRetrieveUpdateView',
    'UserDesactivateView',
    'UserActivateView',
]