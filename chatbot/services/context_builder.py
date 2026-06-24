"""
ContextBuilder — construye el bloque de sistema que se inyecta al LLM.
Usa los modelos y selectores reales del proyecto; no toca nada ajeno.

App names confirmados desde los comentarios en los archivos de modelos:
  users            → users.models.user
  ficha            → ficha.models.ficha_model / ficha_estudiante_model
  docentes         → docentes.models.docente_model / disponibilidad / habilitacion
  bhorario         → bhorario.models.bloque_horario_model
  competencia      → competencia.models.competencia_model
  aulas            → aulas.models.aula_model / bloque_model
  programa         → programa.models.programa_model / version_programa_model
  alertas          → alertas.models.alerta_model
  planificacion    → planificacion.models.bloque_competencia_model
"""

from datetime import date

from users.models.user import User

# BloqueHorario usa TextChoices → dia_semana es 'LUNES', 'MARTES', etc.
_DIA_MAP = {
    0: 'LUNES',
    1: 'MARTES',
    2: 'MIERCOLES',
    3: 'JUEVES',
    4: 'VIERNES',
    5: 'SABADO',
}
_DIA_LABEL = {
    'LUNES': 'Lunes', 'MARTES': 'Martes', 'MIERCOLES': 'Miércoles',
    'JUEVES': 'Jueves', 'VIERNES': 'Viernes', 'SABADO': 'Sábado',
}


def _hoy():
    hoy = date.today()
    dia_str = _DIA_MAP.get(hoy.weekday(), '')
    dia_label = _DIA_LABEL.get(dia_str, dia_str)
    return dia_str, f"{dia_label} {hoy.strftime('%d/%m/%Y')}"


# ─────────────────────────────────────────────────────────────────────────────
# ESTUDIANTE
# ─────────────────────────────────────────────────────────────────────────────

def _contexto_estudiante(user) -> str:
    lines = [
        f"El usuario es ESTUDIANTE: {user.nombre_completo} ({user.email}).",
        "Solo debes responder con información relacionada a su ficha, "
        "horario y datos académicos personales. No reveles datos de otros estudiantes.",
    ]

    # ── Ficha activa ──────────────────────────────────────────────────────────
    try:
        from ficha.models.ficha_estudiante_model import FichaEstudiante

        fe = (
            FichaEstudiante.objects
            .select_related(
                'ficha__version__programa',
                'ficha__jefe_grupo__user',
            )
            .get(estudiante=user, activo=True)
        )
        ficha = fe.ficha
        jefe = (
            ficha.jefe_grupo.user.nombre_completo
            if ficha.jefe_grupo else 'sin asignar'
        )
        programa = ficha.version.programa

        lines += [
            "",
            "── FICHA ACTIVA ──",
            f"Código ficha          : {ficha.codigo_ficha}",
            f"Programa              : {programa.nombre}",
            f"Nivel                 : {programa.get_nivel_display()}",
            f"Versión               : {ficha.version.numero}",
            f"Etapa                 : {ficha.get_etapa_display()}",
            f"Trimestre actual      : {ficha.trimestre}",
            f"Jornada               : {ficha.get_jornada_display()}",
            f"Jefe de grupo         : {jefe}",
            f"Estado ficha          : {ficha.get_estado_display()}",
            f"Fecha inicio          : {ficha.fecha_inicio.strftime('%d/%m/%Y')}",
            f"Estudiantes activos   : {ficha.numero_estudiantes_real}",
            f"Cadena de formación   : {'Sí' if ficha.cadena_formacion else 'No'}",
            f"Trimestres restantes  : {ficha.trimestres_restantes}",
        ]

        # ── Horario hoy ───────────────────────────────────────────────────────
        dia_str, dia_label = _hoy()
        _bloques_hoy(lines, dia_label,
                     ficha_id=ficha.pk, dia_str=dia_str)

        # ── Horario semanal ───────────────────────────────────────────────────
        _horario_semanal_ficha(lines, ficha_id=ficha.pk)

    except FichaEstudiante.DoesNotExist:
        lines.append(
            "\nNo tienes una ficha activa asignada en este momento."
        )
    except Exception as e:
        lines.append(f"\n(Error al obtener ficha: {e})")

    # ── Alertas personales pendientes ─────────────────────────────────────────
    try:
        from alertas.models.alerta_model import Alerta
        alertas = (
            Alerta.objects
            .filter(destinatario=user, estado=Alerta.EstadoAlerta.PENDIENTE)
            .order_by('-fecha_creacion')[:5]
        )
        if alertas.exists():
            lines.append("\n── ALERTAS PENDIENTES ──")
            for a in alertas:
                lines.append(
                    f"  • [{a.get_tipo_display()}] {a.descripcion[:120]}"
                )
    except Exception:
        pass

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# DOCENTE
# ─────────────────────────────────────────────────────────────────────────────

def _contexto_docente(user) -> str:
    lines = [
        f"El usuario es DOCENTE: {user.nombre_completo} ({user.email}).",
        "Puedes darle información sobre sus asignaciones, fichas, "
        "estudiantes y horario.",
    ]

    try:
        from docentes.models.docente_model import Docente

        docente = (
            Docente.objects
            .select_related('user')
            .get(user=user, estado=True)
        )

        lines += [
            "",
            "── PERFIL DOCENTE ──",
            f"Especialidad             : {docente.especialidad}",
            f"Horas máx. semanales     : {docente.horas_max_semanales}",
            f"Horas máx. efectivas     : {docente.horas_max_efectivas}",
            f"Horas asignadas/semana   : {docente.horas_asignadas_semana}",
            f"Sobrecargado             : {'Sí' if docente.esta_sobrecargado else 'No'}",
            f"Permite horas extra      : {'Sí' if docente.permite_horas_extra else 'No'}",
        ]

        # ── Horario hoy ───────────────────────────────────────────────────────
        dia_str, dia_label = _hoy()
        _bloques_hoy(lines, dia_label,
                     docente_id=docente.pk, dia_str=dia_str)

        # ── Horario semanal ───────────────────────────────────────────────────
        _horario_semanal_docente(lines, docente_id=docente.pk)

        # ── Fichas con estudiantes ────────────────────────────────────────────
        _fichas_del_docente(lines, docente)

        # ── Habilitaciones ────────────────────────────────────────────────────
        _habilitaciones(lines, docente)

        # ── Disponibilidad declarada ───────────────────────────────────────────
        _disponibilidad(lines, docente)

        # ── Alertas pendientes ────────────────────────────────────────────────
        try:
            from alertas.models.alerta_model import Alerta
            alertas = (
                Alerta.objects
                .filter(destinatario=user, estado=Alerta.EstadoAlerta.PENDIENTE)
                .order_by('-fecha_creacion')[:5]
            )
            if alertas.exists():
                lines.append("\n── ALERTAS PENDIENTES ──")
                for a in alertas:
                    lines.append(
                        f"  • [{a.get_tipo_display()}] {a.descripcion[:120]}"
                    )
        except Exception:
            pass

    except Exception as e:
        lines.append(f"\n(Error al obtener perfil docente: {e})")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN / COORDINADOR
# ─────────────────────────────────────────────────────────────────────────────

def _contexto_admin(user) -> str:
    lines = [
        f"El usuario es {user.get_rol_display().upper()}: "
        f"{user.nombre_completo} ({user.email}).",
        "Tienes acceso completo al sistema. Puedes consultar cualquier dato.",
    ]

    dia_str, dia_label = _hoy()

    # ── Fichas activas ────────────────────────────────────────────────────────
    try:
        from ficha.models.ficha_model import Ficha

        fichas = (
            Ficha.objects
            .filter(estado=Ficha.Estado.ACTIVA)
            .select_related('version__programa', 'jefe_grupo__user')
            .order_by('codigo_ficha')
        )
        lines.append(f"\n── FICHAS ACTIVAS ({fichas.count()}) ──")
        for f in fichas:
            jefe = (
                f.jefe_grupo.user.nombre_completo
                if f.jefe_grupo else 'sin asignar'
            )
            lines.append(
                f"  • {f.codigo_ficha} | {f.version.programa.nombre} "
                f"v{f.version.numero} | Etapa: {f.get_etapa_display()} | "
                f"Trim. {f.trimestre} | Jornada: {f.get_jornada_display()} | "
                f"Estudiantes: {f.numero_estudiantes_real} | "
                f"Jefe: {jefe}"
            )
    except Exception as e:
        lines.append(f"\n(Error fichas: {e})")

    # ── Docentes activos ──────────────────────────────────────────────────────
    try:
        from docentes.selectors.docente_selector import get_docentes_con_horas_anotadas
        from docentes.selectors.docente_selector import get_horas_anotadas

        docentes = get_docentes_con_horas_anotadas()
        lines.append(f"\n── DOCENTES ACTIVOS ({docentes.count()}) ──")
        for d in docentes:
            horas = get_horas_anotadas(d)
            lines.append(
                f"  • {d.user.nombre_completo} ({d.user.email}) | "
                f"{d.especialidad} | "
                f"Horas: {horas}/{d.horas_max_efectivas} | "
                f"{'⚠ SOBRECARGADO' if horas > d.horas_max_efectivas else 'OK'}"
            )
    except Exception as e:
        lines.append(f"\n(Error docentes: {e})")

    # ── Aulas ─────────────────────────────────────────────────────────────────
    try:
        from aulas.models.aula_model import Aula

        aulas = (
            Aula.objects
            .filter(estado=Aula.Estado.ACTIVA)
            .select_related('bloque')
            .order_by('bloque__nombre', 'codigo_aula')
        )
        lines.append(f"\n── AULAS ACTIVAS ({aulas.count()}) ──")
        for a in aulas:
            lines.append(
                f"  • {a.codigo_aula} | Bloque: {a.bloque.nombre} "
                f"piso {a.piso} | Cap. {a.capacidad} | "
                f"{a.get_tipo_aula_display()}"
            )
    except Exception as e:
        lines.append(f"\n(Error aulas: {e})")

    # ── Bloques hoy (global) ──────────────────────────────────────────────────
    try:
        from bhorario.models.bloque_horario_model import BloqueHorario

        bloques_hoy = (
            BloqueHorario.objects
            .filter(dia_semana=dia_str, es_recurrente=True)
            .select_related(
                'ficha__version__programa',
                'docente__user',
                'aula__bloque',
                'competencia',
            )
            .order_by('hora_inicio')
        )
        lines.append(
            f"\n── CLASES HOY ({dia_label}) — {bloques_hoy.count()} bloques ──"
        )
        for b in bloques_hoy:
            ficha_str  = f"Ficha {b.ficha.codigo_ficha}" if b.ficha else 'sin ficha'
            doc_str    = b.docente.user.nombre_completo if b.docente else 'sin docente'
            aula_str   = b.aula.codigo_aula if b.aula else 'sin aula'
            comp_str   = b.competencia.nombre if b.competencia else 'sin competencia'
            lines.append(
                f"  • {b.hora_inicio.strftime('%H:%M')}–"
                f"{b.hora_fin.strftime('%H:%M')} | "
                f"{ficha_str} | {comp_str} | "
                f"Docente: {doc_str} | Aula: {aula_str}"
            )
    except Exception as e:
        lines.append(f"\n(Error bloques hoy: {e})")

    # ── Alertas del sistema (recientes) ──────────────────────────────────────
    try:
        from alertas.models.alerta_model import Alerta

        alertas = (
            Alerta.objects
            .filter(estado=Alerta.EstadoAlerta.PENDIENTE)
            .select_related('destinatario')
            .order_by('-fecha_creacion')[:10]
        )
        if alertas.exists():
            lines.append(f"\n── ALERTAS PENDIENTES ({alertas.count()}) ──")
            for a in alertas:
                dest = a.destinatario.nombre_completo if a.destinatario else 'sistema'
                lines.append(
                    f"  • [{a.get_tipo_display()}] → {dest}: "
                    f"{a.descripcion[:100]}"
                )
    except Exception as e:
        lines.append(f"\n(Error alertas: {e})")

    # ── Usuarios totales por rol ───────────────────────────────────────────────
    try:
        totales = (
            User.objects
            .filter(is_active=True)
            .values('rol')
            .annotate(total=__import__('django.db.models', fromlist=['Count']).Count('id'))
        )
        lines.append("\n── USUARIOS ACTIVOS POR ROL ──")
        for t in totales:
            lines.append(f"  • {t['rol']}: {t['total']}")
    except Exception:
        pass

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────────────────────────────────────

def _bloques_hoy(lines: list, dia_label: str, dia_str: str,
                 ficha_id: int = None, docente_id: int = None):
    """Agrega los bloques de hoy al bloque de texto según filtro."""
    try:
        from bhorario.models.bloque_horario_model import BloqueHorario

        qs = BloqueHorario.objects.filter(
            dia_semana=dia_str,
            es_recurrente=True,
        ).select_related('aula__bloque', 'docente__user', 'ficha', 'competencia')

        if ficha_id:
            qs = qs.filter(ficha_id=ficha_id)
        if docente_id:
            qs = qs.filter(docente_id=docente_id)

        qs = qs.order_by('hora_inicio')

        lines.append(f"\n── CLASES HOY ({dia_label}) ──")
        if qs.exists():
            for b in qs:
                aula_str = (
                    f"{b.aula.codigo_aula} (Bloque {b.aula.bloque.nombre})"
                    if b.aula else 'sin aula'
                )
                comp_str = b.competencia.nombre if b.competencia else 'sin competencia'
                if ficha_id:
                    # vista estudiante: muestra docente
                    doc_str = (
                        b.docente.user.nombre_completo
                        if b.docente else 'sin docente'
                    )
                    lines.append(
                        f"  • {b.hora_inicio.strftime('%H:%M')}–"
                        f"{b.hora_fin.strftime('%H:%M')} | "
                        f"{comp_str} | Aula: {aula_str} | "
                        f"Docente: {doc_str}"
                    )
                else:
                    # vista docente: muestra ficha
                    ficha_str = (
                        f"Ficha {b.ficha.codigo_ficha}"
                        if b.ficha else 'sin ficha'
                    )
                    lines.append(
                        f"  • {b.hora_inicio.strftime('%H:%M')}–"
                        f"{b.hora_fin.strftime('%H:%M')} | "
                        f"{comp_str} | {ficha_str} | Aula: {aula_str}"
                    )
        else:
            lines.append("  Sin clases programadas para hoy.")
    except Exception as e:
        lines.append(f"  (Error bloques hoy: {e})")


def _horario_semanal_ficha(lines: list, ficha_id: int):
    try:
        from bhorario.models.bloque_horario_model import BloqueHorario

        semana = (
            BloqueHorario.objects
            .filter(ficha_id=ficha_id, es_recurrente=True)
            .select_related('aula__bloque', 'docente__user', 'competencia')
            .order_by('orden_dia', 'hora_inicio')
        )
        if semana.exists():
            lines.append("\n── HORARIO SEMANAL COMPLETO ──")
            dia_actual = None
            for b in semana:
                if b.dia_semana != dia_actual:
                    dia_actual = b.dia_semana
                    lines.append(f"  {_DIA_LABEL.get(dia_actual, dia_actual)}:")
                aula_str = b.aula.codigo_aula if b.aula else 'sin aula'
                comp_str = b.competencia.nombre if b.competencia else 'sin competencia'
                doc_str  = (
                    b.docente.user.nombre_completo
                    if b.docente else 'sin docente'
                )
                lines.append(
                    f"    {b.hora_inicio.strftime('%H:%M')}–"
                    f"{b.hora_fin.strftime('%H:%M')} | "
                    f"{comp_str} | {doc_str} | Aula {aula_str}"
                )
    except Exception as e:
        lines.append(f"  (Error horario semanal: {e})")


def _horario_semanal_docente(lines: list, docente_id: int):
    try:
        from bhorario.models.bloque_horario_model import BloqueHorario

        semana = (
            BloqueHorario.objects
            .filter(docente_id=docente_id, es_recurrente=True)
            .select_related('aula__bloque', 'ficha__version__programa', 'competencia')
            .order_by('orden_dia', 'hora_inicio')
        )
        if semana.exists():
            lines.append("\n── HORARIO SEMANAL COMPLETO ──")
            dia_actual = None
            for b in semana:
                if b.dia_semana != dia_actual:
                    dia_actual = b.dia_semana
                    lines.append(f"  {_DIA_LABEL.get(dia_actual, dia_actual)}:")
                aula_str  = b.aula.codigo_aula if b.aula else 'sin aula'
                comp_str  = b.competencia.nombre if b.competencia else 'sin comp.'
                ficha_str = (
                    f"Ficha {b.ficha.codigo_ficha} "
                    f"({b.ficha.version.programa.nombre})"
                    if b.ficha else 'sin ficha'
                )
                lines.append(
                    f"    {b.hora_inicio.strftime('%H:%M')}–"
                    f"{b.hora_fin.strftime('%H:%M')} | "
                    f"{comp_str} | {ficha_str} | Aula {aula_str}"
                )
    except Exception as e:
        lines.append(f"  (Error horario semanal: {e})")


def _fichas_del_docente(lines: list, docente):
    try:
        from ficha.models.ficha_model import Ficha
        from ficha.models.ficha_estudiante_model import FichaEstudiante

        # Fichas que el docente dicta (via BloqueHorario) activas
        ficha_ids = (
            docente.bloques_horario
            .filter(ficha__isnull=False)
            .values_list('ficha_id', flat=True)
            .distinct()
        )
        fichas = (
            Ficha.objects
            .filter(pk__in=ficha_ids, estado=Ficha.Estado.ACTIVA)
            .select_related('version__programa', 'jefe_grupo__user')
        )

        if fichas.exists():
            lines.append("\n── FICHAS A CARGO ──")
            for f in fichas:
                estudiantes = (
                    FichaEstudiante.objects
                    .filter(ficha=f, activo=True)
                    .select_related('estudiante')
                    .order_by('estudiante__apellido', 'estudiante__nombre')
                )
                lines.append(
                    f"\n  Ficha {f.codigo_ficha} — "
                    f"{f.version.programa.nombre} | "
                    f"Trim. {f.trimestre} | "
                    f"{estudiantes.count()} estudiantes activos:"
                )
                for fe in estudiantes[:60]:
                    lines.append(
                        f"    - {fe.estudiante.nombre_completo} "
                        f"({fe.estudiante.email})"
                    )
    except Exception as e:
        lines.append(f"\n(Error fichas del docente: {e})")


def _habilitaciones(lines: list, docente):
    try:
        from docentes.models.docente_habilitacion_model import HabilitacionDocente

        habs = (
            HabilitacionDocente.objects
            .filter(docente=docente, activo=True)
            .select_related('modulo', 'asignatura')
            .order_by('nivel')
        )
        if habs.exists():
            lines.append("\n── HABILITACIONES ACTIVAS ──")
            for h in habs:
                target = h.modulo or h.asignatura or '(sin asignar)'
                lines.append(
                    f"  • {h.get_nivel_display()}: {target}"
                )
    except Exception as e:
        lines.append(f"\n(Error habilitaciones: {e})")


def _disponibilidad(lines: list, docente):
    try:
        from docentes.models.docente_disponibilidad_model import Disponibilidad

        disps = (
            Disponibilidad.objects
            .filter(docente=docente)
            .order_by('dia_semana', 'hora_inicio')
        )
        if disps.exists():
            lines.append("\n── DISPONIBILIDAD DECLARADA ──")
            for d in disps:
                estado = 'Disponible' if d.disponible else f'NO disponible ({d.motivo[:60]})'
                lines.append(
                    f"  • {_DIA_LABEL.get(d.dia_semana, d.dia_semana)} "
                    f"{d.hora_inicio.strftime('%H:%M')}–"
                    f"{d.hora_fin.strftime('%H:%M')} → {estado}"
                )
    except Exception as e:
        lines.append(f"\n(Error disponibilidad: {e})")


# ─────────────────────────────────────────────────────────────────────────────
# Selector público
# ─────────────────────────────────────────────────────────────────────────────

class ContextBuilder:
    @classmethod
    def build(cls, user) -> str:
        rol = user.rol
        if rol == User.Rol.ESTUDIANTE:
            return _contexto_estudiante(user)
        elif rol == User.Rol.DOCENTE:
            return _contexto_docente(user)
        elif rol in (User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO):
            return _contexto_admin(user)
        return (
            f"Usuario: {user.nombre_completo} | "
            f"Rol: {user.get_rol_display()}"
        )