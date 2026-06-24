# bhorario/selectors/bloque_horario_selector.py
from bhorario.models.bloque_horario_model import BloqueHorario
from ficha.models.ficha_estudiante_model import FichaEstudiante


def get_bloques_para_estudiante(user):
    """Retorna bloques de horario de la(s) ficha(s) activa(s) del estudiante."""
    ficha_ids = FichaEstudiante.objects.filter(
        estudiante=user, activo=True
    ).values_list('ficha_id', flat=True)
    return BloqueHorario.objects.filter(
        ficha_id__in=ficha_ids
    ).select_related('aula', 'docente__user', 'ficha__version__programa')


def get_bloques_para_docente(user):
    """Retorna bloques asignados a un docente."""
    return BloqueHorario.objects.filter(
        docente__user=user
    ).select_related('aula', 'ficha__version__programa')


def get_bloques_con_conflicto(bloque):
    """Retorna bloques que colisionan con el bloque dado (sin incluirlo)."""
    return BloqueHorario.objects.filter(
        dia_semana=bloque.dia_semana,
        hora_inicio__lt=bloque.hora_fin,
        hora_fin__gt=bloque.hora_inicio,
    ).exclude(pk=bloque.pk)