# reportes/services/generators/horario_generator.py
from reportes.services.generators.base_generator import BaseReportGenerator


class HorarioReportGenerator(BaseReportGenerator):
    titulo_reporte = 'Reporte de Horarios'
    nombre_hoja    = 'Horarios'

    def _get_queryset(self):
        from bhorario.models.bloque_horario_model import BloqueHorario
        qs = BloqueHorario.objects.select_related(
            'docente__user', 'aula', 'ficha__version__programa'
        ).order_by('dia_semana', 'hora_inicio')

        if self.filtros.get('dia_semana'):
            qs = qs.filter(dia_semana=self.filtros['dia_semana'])
        if self.filtros.get('jornada'):
            qs = qs.filter(jornada=self.filtros['jornada'])
        if self.filtros.get('ficha_id'):
            qs = qs.filter(ficha_id=self.filtros['ficha_id'])
        if self.filtros.get('docente_id'):
            qs = qs.filter(docente_id=self.filtros['docente_id'])
        return qs

    def _get_headers(self):
        return [
            'Día', 'Hora inicio', 'Hora fin', 'Jornada',
            'Docente', 'Aula', 'Ficha', 'Programa',
        ]

    def _get_row(self, bloque):
        return [
            bloque.get_dia_semana_display(),
            bloque.hora_inicio.strftime('%H:%M'),
            bloque.hora_fin.strftime('%H:%M'),
            bloque.get_jornada_display(),
            bloque.docente.nombre_completo if bloque.docente else '—',
            bloque.aula.codigo_aula        if bloque.aula     else '—',
            bloque.ficha.codigo_ficha      if bloque.ficha    else '—',
            bloque.ficha.version.programa.nombre if bloque.ficha else '—',
        ]