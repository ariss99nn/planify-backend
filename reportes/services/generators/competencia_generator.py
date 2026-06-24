# reportes/services/generators/competencia_generator.py
from reportes.services.generators.base_generator import BaseReportGenerator


class CompetenciaReportGenerator(BaseReportGenerator):
    titulo_reporte = 'Reporte de Competencias y Resultados de Aprendizaje'
    nombre_hoja    = 'Competencias'

    def _get_queryset(self):
        from competencia.models.competencia_model import Competencia
        qs = Competencia.objects.select_related(
            'asignatura__modulo__version__programa'
        ).prefetch_related('resultados_aprendizaje')

        if self.filtros.get('programa_id'):
            qs = qs.filter(
                asignatura__modulo__version__programa_id=self.filtros['programa_id']
            )
        return qs

    def _get_headers(self):
        return [
            'Programa', 'Módulo', 'Asignatura',
            'Competencia', 'Tipo', 'Horas', 'RAPs',
        ]

    def _get_row(self, comp):
        return [
            comp.asignatura.modulo.version.programa.nombre,
            comp.asignatura.modulo.nombre,
            comp.asignatura.nombre,
            comp.descripcion,
            comp.get_tipo_display(),
            comp.horas_totales,
            comp.resultados_aprendizaje.count(),
        ]