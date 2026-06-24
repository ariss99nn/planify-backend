# aulas/apps.py
from django.apps import AppConfig


class AulasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aulas'
    verbose_name = 'Aulas'

    def ready(self):
        from core.signals.image_cleanup import conectar_limpieza_imagen
        from aulas.models.aula_model import Aula
        from aulas.models.bloque_model import Bloque
        from aulas.models.equipamiento_model import Equipamiento

        # Los tres modelos de aulas tienen ImageField
        conectar_limpieza_imagen(Aula,         'imagen')
        conectar_limpieza_imagen(Bloque,       'imagen')
        conectar_limpieza_imagen(Equipamiento, 'imagen')