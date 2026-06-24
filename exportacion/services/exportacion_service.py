# exportacion/services/exportacion_service.py
import csv
import io


class ExportacionService:
    """
    Exporta datos de cualquier módulo a CSV o Excel.
    Sin Celery — respuesta directa (CSV/XLSX son livianos).
    Para archivos masivos usar la tarea async de reportes/.

    CORRECCIÓN: se agregaron los exportadores faltantes:
    ESTUDIANTES, AULAS, PLANES, COMPETENCIAS.
    El modelo RegistroExportacion declaraba 9 tipos pero solo
    3 tenían implementación.
    """

    _FORMULA_TRIGGERS = ('=', '+', '-', '@')

    # ── Validación de choices ─────────────────────────────────────────────────

    @staticmethod
    def _validar_choice(valor, choices_class, campo):
        if valor not in choices_class.values:
            raise ValueError(
                f'Valor "{valor}" no es válido para el filtro "{campo}".'
            )

    # ── Exportadores por módulo ───────────────────────────────────────────────

    @staticmethod
    def exportar_fichas(filtros: dict) -> tuple:
        from ficha.models.ficha_model import Ficha
        from django.db.models import Count, Q

        qs = (
            Ficha.objects
            .select_related('version__programa', 'jefe_grupo')
            .filter(estado=Ficha.Estado.ACTIVA)
            .annotate(
                estudiantes_activos_count=Count(
                    'estudiantes', filter=Q(estudiantes__activo=True)
                )
            )
        )
        if filtros.get('etapa'):
            ExportacionService._validar_choice(filtros['etapa'], Ficha.Etapa, 'etapa')
            qs = qs.filter(etapa=filtros['etapa'])
        if filtros.get('jornada'):
            ExportacionService._validar_choice(filtros['jornada'], Ficha.Jornada, 'jornada')
            qs = qs.filter(jornada=filtros['jornada'])

        headers = [
            'codigo_ficha', 'programa', 'version', 'etapa',
            'trimestre', 'jornada', 'estudiantes_estimados',
            'estudiantes_reales', 'jefe_grupo',
            'fecha_inicio', 'fecha_finalizacion',
        ]
        rows = [
            [
                f.codigo_ficha,
                f.version.programa.nombre,
                f.version.numero,
                f.get_etapa_display(),
                f.trimestre,
                f.get_jornada_display(),
                f.numero_estudiantes_estimado,
                f.estudiantes_activos_count,
                f.jefe_grupo.nombre_completo if f.jefe_grupo else '',
                f.fecha_inicio.isoformat()       if f.fecha_inicio       else '',
                f.fecha_finalizacion.isoformat() if f.fecha_finalizacion else '',
            ]
            for f in qs
        ]
        return headers, rows

    @staticmethod
    def exportar_estudiantes(filtros: dict) -> tuple:
        """
        NUEVO: exporta FichaEstudiante con datos del estudiante y ficha.
        """
        from ficha.models.ficha_estudiante_model import FichaEstudiante

        qs = FichaEstudiante.objects.select_related(
            'estudiante', 'ficha__version__programa'
        )
        if filtros.get('activo') is not None:
            qs = qs.filter(activo=filtros['activo'])
        if filtros.get('ficha_id'):
            qs = qs.filter(ficha_id=filtros['ficha_id'])
        if filtros.get('programa_id'):
            qs = qs.filter(ficha__version__programa_id=filtros['programa_id'])

        headers = [
            'nombre', 'apellido', 'email', 'documento',
            'ficha', 'programa', 'activo', 'motivo_retiro', 'fecha_retiro',
        ]
        rows = [
            [
                fe.estudiante.nombre,
                fe.estudiante.apellido,
                fe.estudiante.email,
                getattr(fe.estudiante, 'numero_documento', ''),
                fe.ficha.codigo_ficha,
                fe.ficha.version.programa.nombre,
                'Sí' if fe.activo else 'No',
                fe.get_motivo_retiro_display() if fe.motivo_retiro else '',
                fe.fecha_retiro.isoformat() if fe.fecha_retiro else '',
            ]
            for fe in qs
        ]
        return headers, rows

    @staticmethod
    def exportar_docentes(filtros: dict) -> tuple:
        from docentes.models.docente_model import Docente

        qs = Docente.objects.select_related('user').filter(estado=True)
        if filtros.get('especialidad'):
            qs = qs.filter(especialidad__icontains=filtros['especialidad'])

        headers = [
            'nombre_completo', 'email', 'especialidad',
            'horas_max_semanales', 'permite_horas_extra',
        ]
        rows = [
            [
                d.nombre_completo,
                d.email,
                d.especialidad,
                d.horas_max_semanales,
                'Sí' if d.permite_horas_extra else 'No',
            ]
            for d in qs
        ]
        return headers, rows

    @staticmethod
    def exportar_horarios(filtros: dict) -> tuple:
        from bhorario.models.bloque_horario_model import BloqueHorario

        qs = BloqueHorario.objects.select_related(
            'docente__user', 'aula', 'ficha__version__programa'
        ).order_by('dia_semana', 'hora_inicio')

        if filtros.get('dia_semana'):
            ExportacionService._validar_choice(
                filtros['dia_semana'], BloqueHorario.DiaSemana, 'dia_semana'
            )
            qs = qs.filter(dia_semana=filtros['dia_semana'])
        if filtros.get('jornada'):
            ExportacionService._validar_choice(
                filtros['jornada'], BloqueHorario.Jornada, 'jornada'
            )
            qs = qs.filter(jornada=filtros['jornada'])
        if filtros.get('ficha_id'):
            qs = qs.filter(ficha_id=filtros['ficha_id'])

        headers = [
            'dia', 'hora_inicio', 'hora_fin', 'jornada',
            'docente', 'aula', 'ficha', 'programa',
        ]
        rows = [
            [
                b.get_dia_semana_display(),
                b.hora_inicio.strftime('%H:%M'),
                b.hora_fin.strftime('%H:%M'),
                b.get_jornada_display(),
                b.docente.nombre_completo if b.docente else '',
                b.aula.codigo_aula        if b.aula    else '',
                b.ficha.codigo_ficha      if b.ficha   else '',
                b.ficha.version.programa.nombre if b.ficha else '',
            ]
            for b in qs
        ]
        return headers, rows

    @staticmethod
    def exportar_aulas(filtros: dict) -> tuple:
        """NUEVO: exporta todas las aulas con su bloque y equipamiento."""
        from aulas.models.aula_model import Aula
        from django.db.models import Count

        qs = (
            Aula.objects
            .select_related('bloque')
            .prefetch_related('equipamiento')
            .annotate(total_equipamiento=Count('equipamiento'))
        )
        if filtros.get('estado'):
            ExportacionService._validar_choice(
                filtros['estado'], Aula.Estado, 'estado'
            )
            qs = qs.filter(estado=filtros['estado'])
        if filtros.get('tipo_aula'):
            qs = qs.filter(tipo_aula=filtros['tipo_aula'])

        headers = [
            'codigo_aula', 'bloque', 'tipo', 'estado',
            'capacidad', 'piso', 'total_equipamiento',
        ]
        rows = [
            [
                a.codigo_aula,
                a.bloque.nombre if a.bloque else '',
                a.get_tipo_aula_display(),
                a.get_estado_display(),
                a.capacidad,
                a.piso,
                a.total_equipamiento,
            ]
            for a in qs
        ]
        return headers, rows

    @staticmethod
    def exportar_planes(filtros: dict) -> tuple:
        """NUEVO: exporta planes trimestrales con ítems y avance."""
        from planificacion.models.plan_trimestral_model import PlanTrimestral
        from django.db.models import Sum

        qs = PlanTrimestral.objects.select_related(
            'ficha__version__programa', 'aprobado_por'
        )
        if filtros.get('estado'):
            qs = qs.filter(estado=filtros['estado'])
        if filtros.get('ficha_id'):
            qs = qs.filter(ficha_id=filtros['ficha_id'])

        headers = [
            'ficha', 'programa', 'trimestre', 'estado',
            'horas_planificadas', 'fecha_inicio', 'fecha_fin', 'aprobado_por',
        ]
        rows = []
        for plan in qs:
            horas = plan.items.aggregate(
                total=Sum('horas_asignadas')
            )['total'] or 0
            rows.append([
                plan.ficha.codigo_ficha,
                plan.ficha.version.programa.nombre,
                plan.trimestre,
                plan.get_estado_display(),
                horas,
                plan.fecha_inicio.isoformat() if plan.fecha_inicio else '',
                plan.fecha_fin.isoformat()    if plan.fecha_fin    else '',
                plan.aprobado_por.nombre_completo if plan.aprobado_por else '',
            ])
        return headers, rows

    @staticmethod
    def exportar_competencias(filtros: dict) -> tuple:
        """NUEVO: exporta competencias y sus RAPs por programa."""
        from competencia.models.competencia_model import Competencia

        qs = Competencia.objects.select_related(
            'asignatura__modulo__version__programa'
        ).prefetch_related('resultados_aprendizaje')

        if filtros.get('programa_id'):
            qs = qs.filter(
                asignatura__modulo__version__programa_id=filtros['programa_id']
            )

        headers = [
            'programa', 'modulo', 'asignatura',
            'competencia', 'tipo', 'horas', 'num_raps',
        ]
        rows = [
            [
                c.asignatura.modulo.version.programa.nombre,
                c.asignatura.modulo.nombre,
                c.asignatura.nombre,
                c.descripcion,
                c.get_tipo_display(),
                c.horas_totales,
                c.resultados_aprendizaje.count(),
            ]
            for c in qs
        ]
        return headers, rows

    # ── Router principal ──────────────────────────────────────────────────────

    @classmethod
    def exportar(cls, modulo: str, filtros: dict) -> tuple:
        handlers = {
            'FICHAS':       cls.exportar_fichas,
            'ESTUDIANTES':  cls.exportar_estudiantes,
            'DOCENTES':     cls.exportar_docentes,
            'HORARIOS':     cls.exportar_horarios,
            'AULAS':        cls.exportar_aulas,
            'PLANES':       cls.exportar_planes,
            'COMPETENCIAS': cls.exportar_competencias,
        }
        handler = handlers.get(modulo)
        if not handler:
            tipos = ', '.join(handlers.keys())
            raise ValueError(
                f'El módulo "{modulo}" no tiene exportador implementado. '
                f'Disponibles: {tipos}'
            )
        return handler(filtros)

    # ── Sanitización ──────────────────────────────────────────────────────────

    @classmethod
    def _prevenir_formula(cls, valor):
        """Previene CSV injection escapando valores que empiecen con =+-@"""
        if isinstance(valor, str) and valor.startswith(cls._FORMULA_TRIGGERS):
            return "'" + valor
        return valor

    @classmethod
    def _sanitizar_filas(cls, rows: list) -> list:
        return [[cls._prevenir_formula(v) for v in row] for row in rows]

    @classmethod
    def a_csv(cls, headers: list, rows: list) -> bytes:
        rows = cls._sanitizar_filas(rows)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(headers)
        writer.writerows(rows)
        return buffer.getvalue().encode('utf-8-sig')

    @classmethod
    def a_excel(cls, headers: list, rows: list) -> bytes:
        try:
            import openpyxl
            from openpyxl.utils.cell import ILLEGAL_CHARACTERS_RE
        except ImportError:
            raise RuntimeError('Instala openpyxl: pip install openpyxl')

        rows = cls._sanitizar_filas(rows)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(headers)
        for row in rows:
            clean = [
                ILLEGAL_CHARACTERS_RE.sub('', v) if isinstance(v, str) else v
                for v in row
            ]
            ws.append(clean)
        buffer = io.BytesIO()
        wb.save(buffer)
        return buffer.getvalue()