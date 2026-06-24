# ficha/apps.py
from django.apps import AppConfig

class FichaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ficha'

    def ready(self):
        import ficha.signals.ficha_signals  # noqa: F401