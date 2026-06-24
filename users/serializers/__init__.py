from users.serializers.user_base_serializer import UserBaseSerializer
from users.serializers.user_read_serializer import UserReadSerializer
from users.serializers.user_self_serializer import UserSelfSerializer
from users.serializers.user_admin_update_serializer import UserAdminUpdateSerializer
from users.serializers.user_profile_update_serializer import UserProfileUpdateSerializer
from users.serializers.user_create_serializer import UserCreateSerializer
from users.serializers.auth.auth_serializer import (
    LoginSerializer,
    LogoutSerializer,)
from users.serializers.auth.email_verification_serializer import EmailVerificationSerializer
from users.serializers.auth.email_change_serializer import (
    EmailChangeRequestSerializer, 
    EmailChangeConfirmSerializer,)

from users.serializers.actions.user_change_role_serializer import UserChangeRoleSerializer
from users.serializers.actions.user_desactivate_serializer import UserDesactivateSerializer
from users.serializers.actions.user_activate_serializer import UserActivateSerializer
from users.serializers.actions.user_username_change_serializer import UsernameChangeSerializer

__all__ = [
    
    # lectura
    'UserBaseSerializer',
    'UserReadSerializer',
    'UserProfileUpdateSerializer',
    'UserAdminReadSerializer',
    # escritura
    'UserCreateSerializer',
    'UserAdminUpdateSerializer',
    'UserSelfSerializer',
    # auth
    'LoginSerializer',
    'LogoutSerializer',
    # email
    'EmailVerificationSerializer',
    'EmailChangeRequestSerializer',
    'EmailChangeConfirmSerializer',
    # password
    'PasswordResetRequestSerializer',
    'PasswordResetConfirmSerializer',

    # admin actions
    'UserChangeRoleSerializer',
    'UserDesactivateSerializer',
    'UserActivateSerializer',
    'UsernameChangeSerializer',
]

