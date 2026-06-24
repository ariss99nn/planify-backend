# core/exceptions.py
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Traduce excepciones de Django (no manejadas nativamente por DRF) a
    respuestas HTTP consistentes, evitando 500 silenciosos.

    Cubre:
    - django.core.exceptions.ValidationError: lanzada por full_clean() en
      Programa, VersionPrograma, Modulo, Asignatura, Ficha,
      HabilitacionDocente cuando una regla de negocio no se replicó (o no
      se pudo replicar a tiempo) en el serializer — p. ej. condiciones
      de carrera entre el .exists() del serializer y el insert real.
    - django.db.IntegrityError: violación de unique_together /
      UniqueConstraint bajo concurrencia.
    - django.db.models.ProtectedError: intento de eliminar un registro
      protegido por on_delete=PROTECT (Programa, VersionPrograma, Modulo,
      Asignatura tienen hijos protegidos).
    """
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            detail = exc.message_dict
        elif hasattr(exc, 'messages'):
            detail = {'detail': exc.messages}
        else:
            detail = {'detail': str(exc)}
        return Response(detail, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, IntegrityError):
        return Response(
            {'detail': 'El registro entra en conflicto con datos existentes. Verifica unicidad e intenta de nuevo.'},
            status=status.HTTP_409_CONFLICT,
        )

    if isinstance(exc, ProtectedError):
        return Response(
            {'detail': 'No se puede eliminar: existen registros relacionados que dependen de este.'},
            status=status.HTTP_409_CONFLICT,
        )

    return drf_exception_handler(exc, context)