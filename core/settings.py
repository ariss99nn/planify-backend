import os

_ENV = os.environ.get('DJANGO_ENV', 'development')

if _ENV == 'production':
    from core.settings.settings_prod import *   # noqa: F401, F403
else:
    from core.settings.settings_dev import *    # noqa: F401, F403
