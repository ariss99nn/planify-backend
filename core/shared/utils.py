# shared/utils.py
from django.utils import timezone
from datetime import timedelta


def get_ip_from_request(request) -> str:
    """Extrae la IP real del cliente considerando proxies reversos."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def calcular_horas_entre(hora_inicio, hora_fin) -> float:
    """Calcula horas decimales entre dos objetos time."""
    minutos = (
        hora_fin.hour * 60 + hora_fin.minute
    ) - (
        hora_inicio.hour * 60 + hora_inicio.minute
    )
    return round(minutos / 60, 1)


def get_semanas_en_rango(fecha_inicio, fecha_fin) -> int:
    """Número de semanas completas entre dos fechas."""
    delta = fecha_fin - fecha_inicio
    return max(1, delta.days // 7)