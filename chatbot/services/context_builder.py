from datetime import date
from django.db.models import Count

from users.models.user import User

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
    dia_str   = _DIA_MAP.get(hoy.weekday(), '')
    dia_label = _DIA_LABEL.get(dia_str, dia_str)
    return dia_str, f"{dia_label} {hoy.strftime('%d/%m/%Y')}"


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _bloques_hoy(lines: list, dia_label: str, dia_str: str,
                 ficha_id: int = None, docente_id: int = None):
    try:
        from bhorario.models.bloque_horario_model import BloqueHorario

        qs = (
            BloqueHorario.objects
            .filter(dia_semana=dia_str, es_recurrente=True)
            .select_related('aula__bloque', 'docente__user', 'ficha', 'competencia')
        )
        if ficha_id:
            qs = qs.filter(ficha_id=ficha_id)
        if docente_id:
            qs = qs.filter(docente_id=docente_id)
        qs = qs.order_by('hora_inicio')

        lines.append(f"\n── CLASES HOY ({dia_label}) ──")
        if qs.exists():
            for b in qs:
                # Aula: Aula.Estado.ACTIVA = 'ACT' — solo mostramos nombre
                aula_str = (
                    f"{b.aula.codigo_aula} (Bloque {b.aula.bloque.nombre})"
                    if b.aula else 'sin aula'
                )
                comp_str = b.competencia.nombre if b.competencia else 'sin competencia'
                if ficha_id:
                    doc_str = (
                        b.docente.user.nombre_completo
                        if b.docente else 'sin docente'
                    )
                    lines.append(
                        f"  • {b.hora_inicio.strftime('%H:%M')}–"
                        f"{b.hora_fin.strftime('%H:%M')} | "
                        f"{comp_str} | Aula: {aula_str} | Docente: {doc_str}"
                    )
                else:
                    ficha_str = f"Ficha {b.ficha.codigo_ficha}" if b.ficha else 'sin ficha'
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

        # orden_dia es un campo real en BloqueHorario (PositiveSmallIntegerField)
        semana = (
            BloqueHorario.objects
            .filter(ficha_id=ficha_id, es_recurrente=True)
            .select_related('aula__bloque', 'docente__user', 'competencia')
            .order_by('orden_dia', 'hora_inicio')
        )
        if not semana.exists():
            return
        lines.append("\n── HORARIO SEMANAL COMPLETO ──")
        dia_actual = None
        for b in semana:
            if b.dia_semana != dia_actual:
                dia_actual = b.dia_semana
                lines.append(f"  {_DIA_LABEL.get(dia_actual, dia_actual)}:")
            aula_str = b.aula.codigo_aula if b.aula else 'sin aula'
            comp_str = b.competencia.nombre if b.competencia else 'sin competencia'
            doc_str  = (
                b.docente.user.nombre_completo if b.docente else 'sin docente'
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
        if not semana.exists():
            return
        lines.append("\n── HORARIO SEMANAL COMPLETO ──")
        dia_actual = None
        for b in semana:
            if b.dia_semana != dia_actual:
                dia_actual = b.dia_semana
                lines.append(f"  {_DIA_LABEL.get(dia_actual, dia_actual)}:")
            aula_str  = b.aula.codigo_aula if b.aula else 'sin aula'
            comp_str  = b.competencia.nombre if b.competencia else 'sin comp.'
            ficha_str = (
                f"Ficha {b.ficha.codigo_ficha} ({b.ficha.version.programa.nombre})"
                if b.ficha else 'sin ficha'
            )
            lines.append(
                f"    {b.hora_inicio.strftime('%H:%M')}–"
                f"{b.hora_fin.strftime('%H:%M')} | "
                f"{comp_str} | {ficha_str} | Aula {aula_str}"
            )
    except Exception as e:
        lines.append(f"  (Error horario semanal docente: {e})")


def _fichas_del_docente(lines: list, docente):
    try:
        from ficha.models.ficha_model import Ficha
        from ficha.models.ficha_estudiante_model import FichaEstudiante

        # related_name en BloqueHorario.docente es 'bloques_horario'
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
        if not fichas.exists():
            return
        lines.append("\n── FICHAS A CARGO ──")
        for f in fichas:
            # related_name en FichaEstudiante.ficha es 'estudiantes'
            estudiantes = (
                FichaEstudiante.objects
                .filter(ficha=f, activo=True)
                .select_related('estudiante')
                .order_by('estudiante__apellido', 'estudiante__nombre')
            )
            lines.append(
                f"\n  Ficha {f.codigo_ficha} — {f.version.programa.nombre} | "
                f"Trim. {f.trimestre} | {estudiantes.count()} estudiantes activos:"
            )
            for fe in estudiantes[:60]:
                # FK en FichaEstudiante se llama 'estudiante', no 'user'
                lines.append(
                    f"    - {fe.estudiante.nombre_completo} ({fe.estudiante.email})"
                )
    except Exception as e:
        lines.append(f"\n(Error fichas del docente: {e})")


def _habilitaciones(lines: list, docente):
    try:
        from docentes.models.docente_habilitacion_model import HabilitacionDocente

        # related_name en HabilitacionDocente.docente es 'habilitaciones'
        habs = (
            HabilitacionDocente.objects
            .filter(docente=docente, activo=True)
            .select_related('modulo', 'asignatura')
            .order_by('nivel')
        )
        if not habs.exists():
            return
        lines.append("\n── HABILITACIONES ACTIVAS ──")
        for h in habs:
            # modulo → programa.Modulo, asignatura → competencia.Asignatura
            # ambos tienen __str__ definido
            target = str(h.modulo) if h.modulo else (
                str(h.asignatura) if h.asignatura else '(sin asignar)'
            )
            lines.append(f"  • {h.get_nivel_display()}: {target}")
    except Exception as e:
        lines.append(f"\n(Error habilitaciones: {e})")


def _disponibilidad(lines: list, docente):
    try:
        from docentes.models.docente_disponibilidad_model import Disponibilidad

        # related_name en Disponibilidad.docente es 'disponibilidades'
        disps = (
            Disponibilidad.objects
            .filter(docente=docente)
            .order_by('dia_semana', 'hora_inicio')
        )
        if not disps.exists():
            return
        lines.append("\n── DISPONIBILIDAD DECLARADA ──")
        for d in disps:
            estado = (
                'Disponible'
                if d.disponible
                else f"NO disponible ({d.motivo[:60]})"
            )
            lines.append(
                f"  • {_DIA_LABEL.get(d.dia_semana, d.dia_semana)} "
                f"{d.hora_inicio.strftime('%H:%M')}–"
                f"{d.hora_fin.strftime('%H:%M')} → {estado}"
            )
    except Exception as e:
        lines.append(f"\n(Error disponibilidad: {e})")


def _alertas_usuario(lines: list, user):
    try:
        from alertas.models.alerta_model import Alerta

        # related_name en Alerta.destinatario es 'alertas'
        alertas = (
            Alerta.objects
            .filter(
                destinatario=user,
                estado=Alerta.EstadoAlerta.PENDIENTE,   # 'PENDIENTE'
            )
            .order_by('-fecha_creacion')[:5]
        )
        if not alertas.exists():
            return
        lines.append("\n── ALERTAS PENDIENTES ──")
        for a in alertas:
            lines.append(f"  • [{a.get_tipo_display()}] {a.descripcion[:120]}")
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# ESTUDIANTE
# ─────────────────────────────────────────────────────────────────────────────

def _contexto_estudiante(user) -> str:
    lines = [
        f"El usuario es ESTUDIANTE: {user.nombre_completo} ({user.email}).",
        "Solo responde con información de su propia ficha y horario. "
        "No reveles datos de otros estudiantes.",
    ]

    try:
        from ficha.models.ficha_estudiante_model import FichaEstudiante

        # Un estudiante solo debe tener una ficha activa (validado en clean())
        # pero usamos first() por si acaso, en vez de get() que lanzaría
        # MultipleObjectsReturned si hay datos inconsistentes.
        fe = (
            FichaEstudiante.objects
            .select_related(
                'ficha__version__programa',
                'ficha__jefe_grupo__user',
            )
            .filter(estudiante=user, activo=True)
            .first()
        )
        if fe is None:
            lines.append("\nNo tienes una ficha activa asignada en este momento.")
            _alertas_usuario(lines, user)
            return "\n".join(lines)

        ficha    = fe.ficha
        programa = ficha.version.programa
        jefe     = (
            ficha.jefe_grupo.user.nombre_completo
            if ficha.jefe_grupo else 'sin asignar'
        )

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

        dia_str, dia_label = _hoy()
        _bloques_hoy(lines, dia_label, dia_str, ficha_id=ficha.pk)
        _horario_semanal_ficha(lines, ficha_id=ficha.pk)

    except Exception as e:
        lines.append(f"\n(Error al obtener ficha: {e})")

    _alertas_usuario(lines, user)
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

        # estado es BooleanField en Docente
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
            # horas_max_efectivas, horas_asignadas_semana y esta_sobrecargado
            # son @property definidas en Docente
            f"Horas máx. efectivas     : {docente.horas_max_efectivas}",
            f"Horas asignadas/semana   : {docente.horas_asignadas_semana}",
            f"Sobrecargado             : {'Sí ⚠' if docente.esta_sobrecargado else 'No'}",
            f"Permite horas extra      : {'Sí' if docente.permite_horas_extra else 'No'}",
        ]

        dia_str, dia_label = _hoy()
        _bloques_hoy(lines, dia_label, dia_str, docente_id=docente.pk)
        _horario_semanal_docente(lines, docente_id=docente.pk)
        _fichas_del_docente(lines, docente)
        _habilitaciones(lines, docente)
        _disponibilidad(lines, docente)

    except Docente.DoesNotExist:
        lines.append("\nNo se encontró perfil de docente activo para este usuario.")
    except Exception as e:
        lines.append(f"\n(Error al obtener perfil docente: {e})")

    _alertas_usuario(lines, user)
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
            .filter(estado=Ficha.Estado.ACTIVA)   # 'ACTIVA'
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
                f"Estudiantes: {f.numero_estudiantes_real} | Jefe: {jefe}"
            )
    except Exception as e:
        lines.append(f"\n(Error fichas: {e})")

    # ── Docentes activos ──────────────────────────────────────────────────────
    try:
        from docentes.selectors.docente_selector import (
            get_docentes_con_horas_anotadas,
            get_horas_anotadas,
        )

        docentes = get_docentes_con_horas_anotadas()
        lines.append(f"\n── DOCENTES ACTIVOS ({docentes.count()}) ──")
        for d in docentes:
            horas     = get_horas_anotadas(d)
            sobrecarga = '⚠ SOBRECARGADO' if horas > d.horas_max_efectivas else 'OK'
            lines.append(
                f"  • {d.user.nombre_completo} ({d.user.email}) | "
                f"{d.especialidad} | "
                f"Horas: {horas}/{d.horas_max_efectivas} | {sobrecarga}"
            )
    except Exception as e:
        lines.append(f"\n(Error docentes: {e})")

    # ── Aulas activas ─────────────────────────────────────────────────────────
    try:
        from aulas.models.aula_model import Aula

        # Aula.Estado.ACTIVA = 'ACT' (TextChoices key)
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

    # ── Bloques de hoy (global) ───────────────────────────────────────────────
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
            ficha_str = f"Ficha {b.ficha.codigo_ficha}" if b.ficha else 'sin ficha'
            doc_str   = b.docente.user.nombre_completo if b.docente else 'sin docente'
            aula_str  = b.aula.codigo_aula if b.aula else 'sin aula'
            comp_str  = b.competencia.nombre if b.competencia else 'sin competencia'
            lines.append(
                f"  • {b.hora_inicio.strftime('%H:%M')}–"
                f"{b.hora_fin.strftime('%H:%M')} | "
                f"{ficha_str} | {comp_str} | "
                f"Docente: {doc_str} | Aula: {aula_str}"
            )
    except Exception as e:
        lines.append(f"\n(Error bloques hoy: {e})")

    # ── Alertas pendientes del sistema ────────────────────────────────────────
    try:
        from alertas.models.alerta_model import Alerta

        alertas = (
            Alerta.objects
            .filter(estado=Alerta.EstadoAlerta.PENDIENTE)  # 'PENDIENTE'
            .select_related('destinatario')
            .order_by('-fecha_creacion')[:10]
        )
        if alertas.exists():
            lines.append(f"\n── ALERTAS PENDIENTES ({alertas.count()}) ──")
            for a in alertas:
                dest = (
                    a.destinatario.nombre_completo
                    if a.destinatario else 'sistema'
                )
                lines.append(
                    f"  • [{a.get_tipo_display()}] → {dest}: "
                    f"{a.descripcion[:100]}"
                )
    except Exception as e:
        lines.append(f"\n(Error alertas: {e})")

    # ── Usuarios activos por rol ──────────────────────────────────────────────
    try:
        # User.is_active (no User.estado — estado es un @property alias)
        totales = (
            User.objects
            .filter(is_active=True)
            .values('rol')
            .annotate(total=Count('id'))
            .order_by('rol')
        )
        lines.append("\n── USUARIOS ACTIVOS POR ROL ──")
        for t in totales:
            lines.append(f"  • {t['rol']}: {t['total']}")
    except Exception as e:
        lines.append(f"\n(Error usuarios: {e})")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# SELECTOR PÚBLICO
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
            f"Usuario: {user.nombre_completo} | Rol: {user.get_rol_display()}"
        )
