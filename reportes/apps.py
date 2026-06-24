# reportes/apps.py
from django.apps import AppConfig


class ReportesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reportes'
    verbose_name = 'Reportes y Novedades'

    def ready(self):
        from reportes.models.reporte_generado_model import ReporteGenerado
        from reportes.services.reporte_factory import ReporteFactory
        from reportes.services.generators.aula_generator import AulaReportGenerator
        from reportes.services.generators.docente_generator import DocenteReportGenerator
        from reportes.services.generators.ficha_generator import FichaReportGenerator
        from reportes.services.generators.horario_generator import HorarioReportGenerator
        from reportes.services.generators.competencia_generator import CompetenciaReportGenerator
        from reportes.services.generators.plan_generator import PlanReportGenerator

        # Tipos originales
        ReporteFactory.registrar(ReporteGenerado.TipoReporte.AULAS,    AulaReportGenerator)
        ReporteFactory.registrar(ReporteGenerado.TipoReporte.DOCENTES,  DocenteReportGenerator)
        ReporteFactory.registrar(ReporteGenerado.TipoReporte.FICHAS,    FichaReportGenerator)

        # Nuevos — cierran el pendiente del comentario original
        ReporteFactory.registrar(ReporteGenerado.TipoReporte.HORARIOS,    HorarioReportGenerator)
        ReporteFactory.registrar(ReporteGenerado.TipoReporte.COMPETENCIAS, CompetenciaReportGenerator)
        ReporteFactory.registrar(ReporteGenerado.TipoReporte.PLANES,       PlanReportGenerator)