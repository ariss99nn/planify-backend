from django.db.models import Count, Q
from reportes.services.generators.base_generator import BaseReportGenerator


class FichaReportGenerator(BaseReportGenerator):
    titulo_reporte = 'Reporte de Fichas'
    nombre_hoja = 'Fichas'

    def _get_queryset(self):
        from ficha.models.ficha_model import Ficha
        qs = Ficha.objects.select_related(
            'version__programa', 'jefe_grupo'
        ).annotate(
            estudiantes_activos_count=Count(
                'estudiantes', filter=Q(estudiantes__activo=True)
            )
        )
        if self.filtros.get('etapa'):
            qs = qs.filter(etapa=self.filtros['etapa'])
        if self.filtros.get('jornada'):
            qs = qs.filter(jornada=self.filtros['jornada'])
        if self.filtros.get('estado') is not None:
            qs = qs.filter(estado=self.filtros['estado'])
        return qs

    def _get_headers(self):
        return ['Código', 'Programa', 'Etapa', 'Trimestre', 'Jornada', 'Estudiantes']

    def _get_row(self, ficha):
        return [
            ficha.codigo_ficha,
            ficha.version.programa.nombre,
            ficha.get_etapa_display(),
            ficha.trimestre,
            ficha.get_jornada_display(),
            ficha.estudiantes_activos_count,
        ]