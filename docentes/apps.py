# docentes/apps.py
from django.apps import AppConfig


class DocentesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'docentes'
    verbose_name = 'Docentes'

    def ready(self):
        # Limpieza automática de imagen del docente al actualizar o borrar
        from core.signals.image_cleanup import conectar_limpieza_imagen
        from docentes.models.docente_model import Docente
        conectar_limpieza_imagen(Docente, 'imagen')