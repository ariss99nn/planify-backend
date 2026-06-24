from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class DjangoValidationErrorMixin:
    """
    Traduce ValidationError de Django (lanzados por full_clean() dentro de
    Model.save()) a ValidationError de DRF, para que el manejador de
    excepciones de DRF responda 400 con detalle por campo en vez de 500.
    """

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(self._format_error(exc))

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(self._format_error(exc))

    @staticmethod
    def _format_error(exc):
        if hasattr(exc, 'message_dict'):
            return exc.message_dict
        return {'non_field_errors': exc.messages}