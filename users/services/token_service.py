import secrets
import uuid


def generate_numeric_code(length: int = 6) -> str:
    """
    Código numérico criptográficamente seguro para verificación por email.
    Retorna un string de `length` dígitos (p.ej. '047382').
    """
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def generate_uuid_token() -> uuid.UUID:
    """
    Token UUID v4 para reset de contraseña.
    Retorna objeto uuid.UUID — compatible con UUIDField de Django.
    El serializer lo recibe como UUIDField y la conversión es automática.
    """
    return uuid.uuid4()