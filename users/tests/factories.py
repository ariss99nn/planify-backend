from django.contrib.auth.models import Group
from users.models import User, EmailVerification, PasswordReset, EmailChangeRequest
from django.utils import timezone
from datetime import timedelta
import uuid


def make_user(
    rol=User.Rol.ESTUDIANTE,
    estado=True,
    email=None,
    password='TestPass123!',
    username=None,
    nombre=None,
    **kwargs,
):
    counter = User.objects.count()
    email = email or f'user_{counter}_{rol.lower()}@test.com'
    username = username or email.split('@')[0]
    nombre = nombre or f'Test {rol.capitalize()}'

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        nombre=nombre,
        rol=rol,
        estado=estado,
        **kwargs,
    )
    return user


def make_coordinador(**kwargs):
    return make_user(rol=User.Rol.COORDINADOR, **kwargs)


def make_administrativo(**kwargs):
    return make_user(rol=User.Rol.ADMIN, **kwargs)


def make_docente(**kwargs):
    return make_user(rol=User.Rol.DOCENTE, **kwargs)


def make_estudiante(**kwargs):
    return make_user(rol=User.Rol.ESTUDIANTE, **kwargs)


def make_verification(user, expired=False, used=False):
    delta = -20 if expired else 10
    return EmailVerification.objects.create(
        user=user,
        code='123456',
        expires_at=timezone.now() + timedelta(minutes=delta),
        is_used=used,
        is_verified=False,
    )


def make_password_reset(user, expired=False, used=False, code='123456'):
    delta = -30 if expired else 60
    return PasswordReset.objects.create(
        user=user,
        token=uuid.uuid4(),
        code=code,
        expires_at=timezone.now() + timedelta(minutes=delta),
        is_used=used,
    )


def make_email_change(user, new_email='nuevo@test.com', expired=False, used=False):
    delta = -20 if expired else 10
    return EmailChangeRequest.objects.create(
        user=user,
        new_email=new_email,
        code='654321',
        expires_at=timezone.now() + timedelta(minutes=delta),
        is_used=used,
    )


def get_auth_header(client, user, password='TestPass123!'):
    """
    Hace login y retorna el header Authorization.
    El usuario debe tener estado=True para poder hacer login.
    """
    response = client.post('/api/auth/login/', {
        'email': user.email,
        'password': password,
    }, content_type='application/json')
    assert 'access' in response.data, (
        f"Login falló para {user.email} (estado={user.estado}): {response.data}"
    )
    token = response.data['access']
    return {'HTTP_AUTHORIZATION': f'Bearer {token}'}


def get_token_for_inactive_user(user, password='TestPass123!'):
    """
    Genera un token JWT directamente sin pasar por el endpoint de login.
    Usar para usuarios con estado=False que necesitan autenticarse en tests
    (ej: verificación de email justo después del registro).
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}