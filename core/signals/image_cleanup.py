# core/signals/image_cleanup.py
"""
Señal pre_save reutilizable para eliminar la imagen anterior
cuando un ImageField es reemplazado en cualquier modelo.

USO — registrar en el apps.py de cada app:

    from core.signals.image_cleanup import conectar_limpieza_imagen
    conectar_limpieza_imagen(MiModelo, 'imagen')

Funciona con almacenamiento local (FileSystemStorage) y en S3
(django-storages S3Boto3Storage) porque usa instance.imagen.delete()
que delega al backend configurado.
"""

import logging
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _borrar_archivo(field_file):
    """
    Borra el archivo físico de un FieldFile si existe.
    No lanza excepción si el archivo ya fue eliminado o no existe.
    """
    if not field_file:
        return
    try:
        storage = field_file.storage
        if storage.exists(field_file.name):
            storage.delete(field_file.name)
            logger.debug("Imagen eliminada: %s", field_file.name)
    except Exception:
        # No propagamos errores de storage para no interrumpir
        # la operación principal. El archivo huérfano puede limpiarse
        # con una tarea de mantenimiento periódica.
        logger.exception("Error al eliminar imagen: %s", getattr(field_file, 'name', '?'))


def _make_pre_save_handler(field_name: str):
    """
    Genera un handler pre_save específico para un campo de imagen.

    Al hacer update de una instancia, compara el valor actual del campo
    en la BD con el valor nuevo que llega. Si son distintos (la imagen
    cambió o fue borrada), elimina el archivo anterior del storage.
    """
    def handler(sender, instance, **kwargs):
        # Instancia nueva (aún no guardada) → no hay archivo anterior
        if not instance.pk:
            return

        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return

        old_file = getattr(old_instance, field_name)
        new_file = getattr(instance, field_name)

        # Si el campo no cambió, no hacer nada
        if not old_file:
            return
        if old_file.name == getattr(new_file, 'name', None):
            return

        # El archivo cambió (o fue vaciado) → borrar el anterior
        _borrar_archivo(old_file)

    handler.__name__ = f'_cleanup_{field_name}_on_update'
    return handler


def _make_post_delete_handler(field_name: str):
    """
    Genera un handler post_delete que elimina el archivo cuando
    se borra el registro completo de la BD.
    """
    def handler(sender, instance, **kwargs):
        field_file = getattr(instance, field_name)
        _borrar_archivo(field_file)

    handler.__name__ = f'_cleanup_{field_name}_on_delete'
    return handler


def conectar_limpieza_imagen(model_class, field_name: str = 'imagen'):
    """
    Conecta las señales pre_save y post_delete al modelo dado
    para el campo de imagen especificado.

    Llamar desde AppConfig.ready() de cada app.

    Args:
        model_class:  La clase del modelo Django (ej. User, Aula).
        field_name:   Nombre del ImageField (default: 'imagen').
    """
    pre_save_handler = _make_pre_save_handler(field_name)
    post_delete_handler = _make_post_delete_handler(field_name)

    pre_save.connect(pre_save_handler, sender=model_class, weak=False)
    post_delete.connect(post_delete_handler, sender=model_class, weak=False)

    logger.debug(
        "Limpieza de imagen '%s' conectada a %s",
        field_name, model_class.__name__,
    )