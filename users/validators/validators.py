import logging
from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

_ALLOWED_FORMATS = {'jpeg', 'png', 'webp'}
_ALLOWED_LABEL   = 'JPG, PNG o WEBP'


def _validate_image_base(image, max_mb: int) -> None:
    """Validación compartida de tamaño y formato real para imágenes."""

    # 1. Tamaño
    if image.size > max_mb * 1024 * 1024:
        raise ValidationError(f'La imagen no puede superar {max_mb} MB.')

    # 2. Formato real via Pillow (no confiar en extensión ni Content-Type)
    try:
        img = Image.open(image)
        fmt = (img.format or '').lower()
        if fmt not in _ALLOWED_FORMATS:
            raise ValidationError(
                f'Formato no permitido. Solo se aceptan imágenes {_ALLOWED_LABEL}.'
            )
    except ValidationError:
        # Re-lanzar ValidationError tal cual — no silenciar errores de negocio.
        raise
    except UnidentifiedImageError:
        # Pillow no pudo identificar el formato — el archivo no es una imagen.
        raise ValidationError('El archivo no es una imagen válida.')
    except (OSError, IOError) as exc:
        # Archivo corrupto o ilegible.
        logger.warning('Error al abrir imagen para validación: %s', exc)
        raise ValidationError('No se pudo leer el archivo de imagen.')
    finally:
        image.seek(0)  # Resetear cursor para que Django pueda guardar el archivo


def validate_imagen(image) -> None:
    """Validador para fotos de perfil de usuario (máx. 2 MB)."""
    _validate_image_base(image, max_mb=2)


def validate_imagen_5mb(image) -> None:
    """Validador para imágenes de aulas y bloques (máx. 5 MB)."""
    _validate_image_base(image, max_mb=5)
