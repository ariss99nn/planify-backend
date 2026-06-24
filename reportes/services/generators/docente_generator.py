from reportes.services.generators.base_generator import BaseReportGenerator


class DocenteReportGenerator(BaseReportGenerator):
    titulo_reporte = 'Reporte de Docentes'
    nombre_hoja = 'Docentes'

    def _get_queryset(self):
        from docentes.models.docente_model import Docente
        qs = Docente.objects.select_related('user').filter(estado=True)
        if self.filtros.get('especialidad'):
            qs = qs.filter(especialidad__icontains=self.filtros['especialidad'])
        return qs

    def _get_headers(self):
        return ['Nombre', 'Email', 'Especialidad', 'Horas máx.']

    def _get_row(self, docente):
        return [
            docente.user.nombre,
            docente.user.email,
            docente.especialidad,
            docente.horas_max_semanales,
        ]