from core.settings.settings_base import *  # noqa: F401, F403
from django.core.exceptions import ImproperlyConfigured

# ──────────────────────────────────────────────────────────────────────────────
# DEBUG — siempre False en producción
# ──────────────────────────────────────────────────────────────────────────────
DEBUG = False

# ──────────────────────────────────────────────────────────────────────────────
# ALLOWED_HOSTS
# SEGURIDAD: default vacío — el deploy DEBE definir la variable.
# ──────────────────────────────────────────────────────────────────────────────
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='')
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS no está configurado. "
        "Define la variable de entorno ALLOWED_HOSTS en producción."
    )

# ──────────────────────────────────────────────────────────────────────────────
# CACHÉ — Redis compartido entre todos los workers
# Necesario para: rate limiting global, ETag middleware, session cache
# ──────────────────────────────────────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND':  'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS':        'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        },
        'KEY_PREFIX': 'backend_cache',
        'TIMEOUT':    300,
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# CHANNELS — Redis Channel Layer (escala horizontal)
# ──────────────────────────────────────────────────────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [config('REDIS_URL', default='redis://localhost:6379/0')],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# HTTP SECURITY HEADERS
# ──────────────────────────────────────────────────────────────────────────────
SECURE_HSTS_SECONDS            = 31_536_000       # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True
SECURE_SSL_REDIRECT            = True
SECURE_PROXY_SSL_HEADER        = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE  = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE   = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

SECURE_CONTENT_TYPE_NOSNIFF  = True
SECURE_BROWSER_XSS_FILTER    = True   # compatibilidad con IE11
X_FRAME_OPTIONS               = 'DENY'

# ──────────────────────────────────────────────────────────────────────────────
# CORS — solo orígenes explícitos en producción
# ──────────────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS   = config('CORS_ALLOWED_ORIGINS', cast=Csv(), default='')

if not CORS_ALLOWED_ORIGINS:
    raise ImproperlyConfigured(
        "CORS_ALLOWED_ORIGINS no está configurado. "
        "Define los orígenes permitidos en producción."
    )

CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', cast=bool, default=False)

# ──────────────────────────────────────────────────────────────────────────────
# EMAIL — backend SMTP en producción
# ──────────────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# ──────────────────────────────────────────────────────────────────────────────
# LOGGING — structured JSON en producción (integra con Datadog/CloudWatch)
# ──────────────────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d',
        },
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level':    config('LOG_LEVEL', default='WARNING'),
    },
    'loggers': {
        'django':         {'handlers': ['console'], 'level': 'ERROR',   'propagate': False},
        'django.security': {'handlers': ['console'], 'level': 'INFO',    'propagate': False},
        'users':          {'handlers': ['console'], 'level': 'INFO',    'propagate': False},
        'audit':          {'handlers': ['console'], 'level': 'INFO',    'propagate': False},
        'celery':         {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
    },
}
