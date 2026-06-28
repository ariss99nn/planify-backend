# users/tests/factories.py
import uuid
from datetime import timedelta

from django.utils import timezone

from users.models import User, EmailVerification, PasswordReset, EmailChangeRequest


def make_user(
    rol=User.Rol.ESTUDIANTE,
    estado=True,
    email=None,
    password='TestPass123!',
    username=None,
    nombre=None,
    apellido='Test',
    email_verificado=None,  # si no se pasa, sigue el estado
    **kwargs,
):
    """
    Crea un User de prueba.

    CORRECCIÓN 1: make_user(estado=True) ahora también pone email_verificado=True
    por defecto, porque el LoginSerializer valida ambos campos.
    Sin email_verificado=True, login() falla aunque is_active sea True.

    CORRECCIÓN 2: el manager acepta `estado` como alias de `is_active`.
    """
    counter = User.objects.count()
    email    = email    or f'user_{counter}_{rol.lower()}@test.com'
    username = username or email.split('@')[0]
    nombre   = nombre   or f'Test {rol.capitalize()}'

    # email_verificado sigue a estado salvo que se especifique explícitamente
    if email_verificado is None:
        email_verificado = estado

    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        nombre=nombre,
        apellido=apellido,
        rol=rol,
        estado=estado,
        email_verificado=email_verificado,
        **kwargs,
    )


def make_coordinador(**kwargs):
    return make_user(rol=User.Rol.COORDINADOR, **kwargs)


def make_administrativo(**kwargs):
    # CORRECCIÓN: User.Rol.ADMIN no existe. El rol es ADMINISTRATIVO.
    return make_user(rol=User.Rol.ADMINISTRATIVO, **kwargs)


def make_docente(**kwargs):
    return make_user(rol=User.Rol.DOCENTE, **kwargs)


def make_estudiante(**kwargs):
    return make_user(rol=User.Rol.ESTUDIANTE, **kwargs)


def make_verification(user, expired=False, used=False):
    """
    Crea un EmailVerification con code='123456'.
    """
    delta = -20 if expired else 10
    return EmailVerification.objects.create(
        user=user,
        code='123456',
        expires_at=timezone.now() + timedelta(minutes=delta),
        is_used=used,
        is_verified=False,
    )


def make_password_reset(user, expired=False, used=False):
    """
    Crea un PasswordReset usando solo los campos que existen en el modelo
    DESPUÉS de la migración 0004 (que eliminó code, expires_at, is_used).

    El modelo final solo tiene: user, token (UUID), created_at, used.
    La expiración se calcula en la property is_expired usando created_at.

    CORRECCIÓN: la versión anterior pasaba code, expires_at e is_used,
    que ya no son campos del modelo → IntegrityError/TypeError en BD.
    """
    if expired:
        # Crear el reset y luego manipular created_at en BD directamente
        reset = PasswordReset.objects.create(user=user, token=uuid.uuid4(), used=used)
        # Retrotraer created_at más de PASSWORD_RESET_EXPIRY_HOURS horas
        from django.conf import settings
        hours = getattr(settings, 'PASSWORD_RESET_EXPIRY_HOURS', 2)
        PasswordReset.objects.filter(pk=reset.pk).update(
            created_at=timezone.now() - timedelta(hours=hours + 1)
        )
        reset.refresh_from_db()
        return reset
    return PasswordReset.objects.create(user=user, token=uuid.uuid4(), used=used)


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

    CORRECCIÓN: URL era /api/v1/auth/login/ — el proyecto real usa /api/auth/login/
    (sin prefijo v1).

    Requiere que el usuario tenga is_active=True Y email_verificado=True,
    de lo contrario LoginSerializer.validate() levanta ValidationError.
    """
    response = client.post(
        '/api/auth/login/',
        {'email': user.email, 'password': password},
        content_type='application/json',
    )
    assert 'access' in response.data, (
        f"Login falló para {user.email} "
        f"(is_active={user.is_active}, email_verificado={user.email_verificado}, "
        f"rol={user.rol}): {response.data}"
    )
    return {'HTTP_AUTHORIZATION': f'Bearer {response.data["access"]}'}


def get_token_for_inactive_user(user):
    """
    Genera JWT directamente sin pasar por login.
    Para usuarios con is_active=False que necesitan autenticarse
    (ej: justo después del registro, antes de verificar el email).
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}