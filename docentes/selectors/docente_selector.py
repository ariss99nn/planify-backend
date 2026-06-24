# docentes/selectors/docente_selector.py
"""
Selectores para consultas complejas del dominio Docente.

Se centraliza aquí la lógica de cálculo de carga horaria en SQL
para evitar el patrón N+1 de llamar horas_asignadas_semana (property)
en un bucle Python sobre cada docente.
"""

from django.db.models import Sum, ExpressionWrapper, F, IntegerField, Q
from django.db.models.functions import ExtractHour, ExtractMinute


def get_docentes_con_horas_anotadas():
    """
    Retorna un QuerySet de Docentes activos con el campo anotado
    `minutos_asignados` calculado directamente en SQL.

    Reemplaza el patrón:
        for docente in Docente.objects.filter(estado=True):
            if docente.esta_sobrecargado:   # ← 1 query por docente (N+1)

    Por una sola query con JOIN + GROUP BY + SUM en PostgreSQL.

    El campo anotado `minutos_asignados` es la suma de
    (hora_fin - hora_inicio) en minutos de todos los bloques
    recurrentes asignados al docente.
    """
    from docentes.models.docente_model import Docente

    return Docente.objects.filter(estado=True).annotate(
        minutos_asignados=Sum(
            ExpressionWrapper(
                (ExtractHour(F('bloques_horario__hora_fin')) * 60
                 + ExtractMinute(F('bloques_horario__hora_fin')))
                - (ExtractHour(F('bloques_horario__hora_inicio')) * 60
                   + ExtractMinute(F('bloques_horario__hora_inicio'))),
                output_field=IntegerField(),
            ),
            filter=Q(bloques_horario__es_recurrente=True),
        )
    ).select_related('user')


def esta_sobrecargado_anotado(docente) -> bool:
    """
    Evalúa si un docente supera su límite usando el campo anotado
    `minutos_asignados` si está disponible en el objeto.

    Cae en la property original (con su propia query) si el objeto
    no viene del queryset anotado — así la función es segura en
    cualquier contexto.
    """
    if hasattr(docente, 'minutos_asignados') and docente.minutos_asignados is not None:
        horas = round(docente.minutos_asignados / 60, 1)
        return horas > docente.horas_max_efectivas
    # Fallback: property original (ejecuta su propia query)
    return docente.esta_sobrecargado


def get_horas_anotadas(docente) -> float:
    """
    Retorna las horas asignadas del docente usando el campo anotado
    si está disponible, o calcula desde la property como fallback.
    """
    if hasattr(docente, 'minutos_asignados') and docente.minutos_asignados is not None:
        return round(docente.minutos_asignados / 60, 1)
    return docente.horas_asignadas_semana