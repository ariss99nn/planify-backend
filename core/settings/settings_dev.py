from core.settings.settings_base import *  # noqa: F401, F403

# ──────────────────────────────────────────────────────────────────────────────
# MODO DEBUG
# ──────────────────────────────────────────────────────────────────────────────
DEBUG = config('DEBUG', default=True, cast=bool)

# ──────────────────────────────────────────────────────────────────────────────
# HOSTS
# En desarrollo se acepta cualquier host para simplificar el setup local.
# ──────────────────────────────────────────────────────────────────────────────
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='*')

# ──────────────────────────────────────────────────────────────────────────────
# CACHÉ — LocMemCache es suficiente para desarrollo (por proceso)
# ──────────────────────────────────────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'dev-cache',
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# CHANNELS — InMemoryChannelLayer es aceptable en desarrollo (1 proceso)
# ──────────────────────────────────────────────────────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# CORS relajado en desarrollo
# ──────────────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True
