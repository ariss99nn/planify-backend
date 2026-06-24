# reportes/services/generators/plan_generator.py
from reportes.services.generators.base_generator import BaseReportGenerator


class PlanReportGenerator(BaseReportGenerator):
    titulo_reporte = 'Reporte de Planes Trimestrales'
    nombre_hoja    = 'Planes'

    def _get_queryset(self):
        from planificacion.models.plan_trimestral_model import PlanTrimestral
        qs = PlanTrimestral.objects.select_related(
            'ficha__version__programa', 'aprobado_por'
        )
        if self.filtros.get('estado'):
            qs = qs.filter(estado=self.filtros['estado'])
        if self.filtros.get('ficha_id'):
            qs = qs.filter(ficha_id=self.filtros['ficha_id'])
        return qs

    def _get_headers(self):
        return [
            'Ficha', 'Programa', 'Trimestre',
            'Estado', 'Fecha inicio', 'Fecha fin',
            'Aprobado por',
        ]

    def _get_row(self, plan):
        return [
            plan.ficha.codigo_ficha,
            plan.ficha.version.programa.nombre,
            plan.trimestre,
            plan.get_estado_display(),
            plan.fecha_inicio.isoformat()   if plan.fecha_inicio else '—',
            plan.fecha_fin.isoformat()      if plan.fecha_fin    else '—',
            plan.aprobado_por.nombre_completo if plan.aprobado_por else '—',
        ]