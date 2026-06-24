# shared/validators.py
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


def validate_horas_positivas(horas_lectivas=None, horas_practicas=None):
    """Validación reutilizable para campos de horas en modelos Django."""
    errors = {}
    if horas_lectivas is not None and horas_lectivas <= 0:
        errors['horas_lectivas'] = 'Las horas lectivas deben ser mayores a 0.'
    if horas_practicas is not None and horas_practicas < 0:
        errors['horas_practicas'] = 'Las horas prácticas no pueden ser negativas.'
    if errors:
        raise DjangoValidationError(errors)


def validate_horas_serializer(horas_lectivas=None, horas_practicas=None):
    """Versión para serializers DRF."""
    errors = {}
    if horas_lectivas is not None and horas_lectivas <= 0:
        errors['horas_lectivas'] = 'Las horas lectivas deben ser mayores a 0.'
    if horas_practicas is not None and horas_practicas < 0:
        errors['horas_practicas'] = 'Las horas prácticas no pueden ser negativas.'
    if errors:
        raise serializers.ValidationError(errors)