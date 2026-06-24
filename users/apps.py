# users/apps.py
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Usuarios'

    def ready(self):
        # Señales de grupos y permisos
        import users.signals.users_signals  # noqa: F401

        # Limpieza automática de imagen al actualizar o borrar usuario
        from core.signals.image_cleanup import conectar_limpieza_imagen
        from users.models.user import User
        conectar_limpieza_imagen(User, 'imagen')