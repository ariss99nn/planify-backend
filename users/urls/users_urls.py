from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views.auth import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ProfileView,
    UsernameChangeView,
    EmailChangeRequestView,
    EmailChangeConfirmView,
    ResendVerificationView,
    CheckEmailExistsView,
)
from users.views.user import (
    UserListCreateView,
    UserRetrieveUpdateView,
    UserDesactivateView,
    UserActivateView,
)

# =============================================================================
# AUTH — /api/auth/
# =============================================================================
auth_urlpatterns = [
    # Registro y verificación
    path('register/',                RegisterView.as_view(),              name='auth-register'),
    path('verify-email/',            VerifyEmailView.as_view(),           name='auth-verify-email'),
    path('resend-verification/',     ResendVerificationView.as_view(),    name='auth-resend-verification'),

    # Login / Logout / Refresh
    path('login/',                   LoginView.as_view(),                 name='auth-login'),
    path('refresh/',                 TokenRefreshView.as_view(),          name='auth-refresh'),
    path('logout/',                  LogoutView.as_view(),                name='auth-logout'),

    # Recuperación de contraseña
    path('password-reset/',          PasswordResetRequestView.as_view(),  name='auth-password-reset'),
    path('password-reset/confirm/',  PasswordResetConfirmView.as_view(),  name='auth-password-reset-confirm'),
    path('check-email/', CheckEmailExistsView.as_view(), name='check-email'),

    # Perfil propio
    path('profile/',                 ProfileView.as_view(),               name='auth-profile'),
    path('profile/username/',        UsernameChangeView.as_view(),        name='auth-profile-username'),
    path('profile/email/',           EmailChangeRequestView.as_view(),    name='auth-profile-email'),
    path('profile/email/confirm/',   EmailChangeConfirmView.as_view(),    name='auth-profile-email-confirm'),
]

# =============================================================================
# USERS — /api/users/
# =============================================================================
user_urlpatterns = [
    # Listado y creación
    path('',                         UserListCreateView.as_view(),        name='user-list-create'),

    # Detalle y actualización
    path('<int:pk>/',                UserRetrieveUpdateView.as_view(),    name='user-detail-update'),

    # Acciones específicas
    path('<int:pk>/rol/',            UserRetrieveUpdateView.as_view(),    {'action': 'rol'},   name='user-change-role'),
    path('<int:pk>/deactivate/',     UserDesactivateView.as_view(),                            name='user-deactivate'),
    path('<int:pk>/activate/',       UserActivateView.as_view(),                              name='user-activate'),
]
