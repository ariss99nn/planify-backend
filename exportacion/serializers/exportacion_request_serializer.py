# exportacion/serializers/exportacion_request_serializer.py
from rest_framework import serializers
from exportacion.models.exportacion_model import RegistroExportacion

# Solo los módulos con handler implementado en ExportacionService.
# Cuando se implemente un nuevo handler, agregar aquí también.
MODULOS_DISPONIBLES = [
    (RegistroExportacion.TipoExportacion.FICHAS,   "Fichas"),
    (RegistroExportacion.TipoExportacion.DOCENTES,  "Docentes"),
    (RegistroExportacion.TipoExportacion.HORARIOS,  "Horarios"),
]

FORMATOS_DISPONIBLES = [
    (RegistroExportacion.Formato.EXCEL, "Excel (.xlsx)"),
    (RegistroExportacion.Formato.CSV,   "CSV"),
]


class ExportacionRequestSerializer(serializers.Serializer):
    modulo = serializers.ChoiceField(choices=MODULOS_DISPONIBLES)
    formato = serializers.ChoiceField(choices=FORMATOS_DISPONIBLES)
    filtros = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=dict,
    )