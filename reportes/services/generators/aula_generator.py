from reportes.services.generators.base_generator import BaseReportGenerator


class AulaReportGenerator(BaseReportGenerator):
    titulo_reporte = 'Reporte de Aulas'
    nombre_hoja = 'Aulas'

    def _get_queryset(self):
        from aulas.models.aula_model import Aula
        qs = Aula.objects.select_related('bloque')
        if self.filtros.get('estado'):
            qs = qs.filter(estado=self.filtros['estado'])
        if self.filtros.get('tipo_aula'):
            qs = qs.filter(tipo_aula=self.filtros['tipo_aula'])
        return qs

    def _get_headers(self):
        return ['Código', 'Bloque', 'Tipo', 'Estado', 'Capacidad']

    def _get_row(self, aula):
        return [
            aula.codigo_aula,
            aula.bloque.nombre if aula.bloque else '—',
            aula.get_tipo_aula_display(),
            aula.get_estado_display(),
            aula.capacidad,
        ]