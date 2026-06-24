import os
from decouple import config, Csv
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────────────────────────────────────
# SEGURIDAD — SECRET_KEY
# ──────────────────────────────────────────────────────────────────────────────
# Obligatoria. Nunca debe tener valor por defecto en código fuente.
SECRET_KEY = config('SECRET_KEY')

# ──────────────────────────────────────────────────────────────────────────────
# AUTH USER MODEL
# ──────────────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'users.User'

# ──────────────────────────────────────────────────────────────────────────────
# INSTALLED APPS
# ──────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'daphne',

    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceros
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'storages',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'django_celery_results',

    # Aplicaciones del proyecto
    'alertas.apps.AlertasConfig',
    'aulas.apps.AulasConfig',
    'bhorario.apps.BhorarioConfig',
    'competencia.apps.CompetenciaConfig',
    'docentes.apps.DocentesConfig',
    'ficha.apps.FichaConfig',
    'programa.apps.ProgramaConfig',
    'users.apps.UsersConfig',
    'planificacion.apps.PlanificacionConfig',
    'reportes.apps.ReportesConfig',
    'notificaciones.apps.NotificacionesConfig',
    'exportacion.apps.ExportacionConfig',
    'analitica.apps.AnaliticaConfig',
    'channels',
]

# ──────────────────────────────────────────────────────────────────────────────
# MIDDLEWARE
# ──────────────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.audit_middleware.AuditMiddleware',
    'core.middleware.rate_limit_middleware.RolBasedRateLimitMiddleware',
    'core.middleware.cache_headers_middleware.ETagMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF    = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'

# ──────────────────────────────────────────────────────────────────────────────
# TEMPLATES
# ──────────────────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# BASE DE DATOS
# PostgreSQL si DB_NAME está definido, SQLite como fallback para desarrollo
# ──────────────────────────────────────────────────────────────────────────────
DB_NAME = config('DB_NAME', default=None)

if DB_NAME:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     DB_NAME,
            'USER':     config('DB_USER',     default=''),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST':     config('DB_HOST',     default='localhost'),
            'PORT':     config('DB_PORT',     default='5432'),
            'CONN_MAX_AGE': 60,   # connection pooling leve
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME':   BASE_DIR / 'db.sqlite3',
        }
    }

# ──────────────────────────────────────────────────────────────────────────────
# DRF
# ──────────────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    # SEGURIDAD: IsAuthenticated como permiso global por defecto.
    # Cualquier endpoint que necesite acceso público debe declararlo
    # explícitamente con AllowAny en su propia permission_classes.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # Paginación por defecto; cada app puede sobreescribirla.
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,

    # Versionado de API por URL (/api/v1/...)
    'DEFAULT_VERSIONING_CLASS':  'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION':           'v1',
    'ALLOWED_VERSIONS':          ['v1'],

    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

# ──────────────────────────────────────────────────────────────────────────────
# JWT
# ──────────────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES':      ('Bearer',),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# ──────────────────────────────────────────────────────────────────────────────
# CORS / CSRF
# ──────────────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL', cast=bool, default=False)

if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv(), default='')

# SEGURIDAD: False por defecto. Activar solo cuando el frontend está en
# un dominio diferente y envía cookies — y siempre con CORS_ALLOWED_ORIGINS
# configurado explícitamente (nunca combinar con CORS_ALLOW_ALL_ORIGINS=True).
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', cast=bool, default=False)

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv(), default='')
CORS_URLS_REGEX = r'^.*$'

# ──────────────────────────────────────────────────────────────────────────────
# EMAIL
# ──────────────────────────────────────────────────────────────────────────────
EMAIL_BACKEND   = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST      = config('EMAIL_HOST',    default='smtp.gmail.com')
EMAIL_PORT      = config('EMAIL_PORT',    cast=int, default=587)
EMAIL_USE_TLS   = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_HOST_USER     = config('EMAIL_HOST_USER',     default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL',  default='noreply@tudominio.com')
FRONTEND_URL        = config('FRONTEND_URL',         default='http://localhost:3000')

# ──────────────────────────────────────────────────────────────────────────────
# STATIC & MEDIA
# ──────────────────────────────────────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

USE_S3 = config('USE_S3', cast=bool, default=False)

if USE_S3:
    AWS_ACCESS_KEY_ID       = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY   = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME      = config('AWS_S3_REGION_NAME')
    AWS_S3_ENDPOINT_URL     = config('AWS_S3_ENDPOINT_URL', default=None)
    AWS_S3_CUSTOM_DOMAIN    = config(
        'AWS_S3_CUSTOM_DOMAIN',
        default=f"{config('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com",
    )
    AWS_S3_FILE_OVERWRITE   = False
    AWS_DEFAULT_ACL         = config('AWS_DEFAULT_ACL', default=None)
    AWS_QUERYSTRING_AUTH    = config('AWS_QUERYSTRING_AUTH', cast=bool, default=False)

    STATIC_LOCATION = config('STATIC_LOCATION', default='static')
    MEDIA_LOCATION  = config('MEDIA_LOCATION',  default='media')

    STATIC_URL = config('STATIC_URL', default=f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/')
    MEDIA_URL  = config('MEDIA_URL',  default=f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/')

    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': {'location': MEDIA_LOCATION},
        },
        'staticfiles': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': {'location': STATIC_LOCATION},
        },
    }
else:
    MEDIA_URL  = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# ──────────────────────────────────────────────────────────────────────────────
# PASSWORD RESET
# ──────────────────────────────────────────────────────────────────────────────
# Nombre unificado: PASSWORD_RESET_EXPIRY_HOURS
# PasswordReset.get_expiration_time() lee este mismo nombre.
# CORRECCIÓN: el nombre anterior (PASSWORD_RESET_EXPIRY_MINUTES) era incorrecto.
PASSWORD_RESET_EXPIRY_HOURS = config('PASSWORD_RESET_EXPIRY_HOURS', cast=int, default=2)

# ──────────────────────────────────────────────────────────────────────────────
# PASSWORD VALIDATORS
# ──────────────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ──────────────────────────────────────────────────────────────────────────────
# API DOCS (drf-spectacular)
# ──────────────────────────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE':       config('API_TITLE',       default='API'),
    'DESCRIPTION': config('API_DESCRIPTION', default='Documentación de la API'),
    'VERSION':     '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SECURITY':    [{'BearerAuth': []}],
    'COMPONENT_SECURITY_SCHEMES': {
        'BearerAuth': {
            'type':        'http',
            'scheme':      'bearer',
            'bearerFormat': 'JWT',
        }
    },
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
        'displayRequestDuration': True,
        'filter': True,
    },
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# CELERY
# ──────────────────────────────────────────────────────────────────────────────
CELERY_BROKER_URL        = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND    = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT    = ['json']
CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'

from celery.schedules import crontab  # noqa: E402

CELERY_BEAT_SCHEDULE = {
    'snapshot-diario': {
        'task':     'analitica.tasks.generar_snapshot_diario',
        'schedule': crontab(hour=2, minute=0),
    },
    'limpiar-reportes': {
        'task':     'reportes.tasks.limpiar_reportes_antiguos',
        'schedule': crontab(hour=3, minute=0),
    },
    'novedades-planificacion': {
        'task':     'planificacion.tasks.generar_novedades_planificacion',
        'schedule': crontab(hour=6, minute=0),
    },
    'novedades-sobrecarga-docentes': {
        'task':     'docentes.tasks.detectar_docentes_sobrecargados',
        'schedule': crontab(hour=6, minute=30),
    },
    'novedades-aulas-conflicto': {
        'task':     'aulas.tasks.detectar_aulas_con_conflicto',
        'schedule': crontab(hour=7, minute=0),
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# CHANNELS — definido en settings_dev.py / settings_prod.py según entorno
# ──────────────────────────────────────────────────────────────────────────────
ASGI_APPLICATION = 'core.asgi.application'

# ──────────────────────────────────────────────────────────────────────────────
# OLLAMA (chatbot RAG)
# ──────────────────────────────────────────────────────────────────────────────
OLLAMA_CONFIG = {
    'BASE_URL':         config('OLLAMA_BASE_URL',  default='http://localhost:11434'),
    'LLM_MODEL':        config('OLLAMA_LLM_MODEL', default='llama3'),
    'EMBEDDING_MODEL':  config('OLLAMA_EMB_MODEL', default='nomic-embed-text'),
    'CHROMA_PERSIST_DIR': os.path.join(BASE_DIR, 'chroma_db'),
}

# ──────────────────────────────────────────────────────────────────────────────
# INTERNACIONALIZACIÓN
# ──────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = config('DJANGO_LANGUAGE_CODE', default='es-co')
TIME_ZONE     = config('DJANGO_TIMEZONE',      default='America/Bogota')
USE_I18N      = True
USE_TZ        = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ──────────────────────────────────────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────────────────────────────────────
LOG_LEVEL = config('LOG_LEVEL', default='INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} — {message}',
            'style':  '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style':  '{',
        },
    },
    'handlers': {
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level':    LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers':  ['console'],
            'level':     'WARNING',
            'propagate': False,
        },
        'users': {
            'handlers':  ['console'],
            'level':     LOG_LEVEL,
            'propagate': False,
        },
        'audit': {
            'handlers':  ['console'],
            'level':     'INFO',
            'propagate': False,
        },
    },
}
