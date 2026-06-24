from django.db import migrations


def forwards(apps, schema_editor):
    Habilitacion = apps.get_model('docentes', 'HabilitacionDocente')

    # Try to get legacy models; they may already be removed in newer branches.
    try:
        DocenteModulo = apps.get_model('programa', 'DocenteModulo')
    except LookupError:
        DocenteModulo = None

    try:
        DocenteAsignatura = apps.get_model('competencia', 'DocenteAsignatura')
    except LookupError:
        DocenteAsignatura = None

    created = 0

    if DocenteModulo is not None:
        for dm in DocenteModulo.objects.all():
            docente_id = getattr(dm, 'docente_id', getattr(dm, 'docente', None))
            modulo_id = getattr(dm, 'modulo_id', getattr(dm, 'modulo', None))
            if not docente_id or not modulo_id:
                continue
            # Evita duplicados activos
            exists = Habilitacion.objects.filter(
                docente_id=docente_id,
                modulo_id=modulo_id,
                nivel='MODULO',
                activo=True,
            ).exists()
            if exists:
                continue
            try:
                Habilitacion.objects.create(
                    docente_id=docente_id,
                    nivel='MODULO',
                    modulo_id=modulo_id,
                    asignatura_id=None,
                    activo=getattr(dm, 'activo', True),
                    fecha_desde=getattr(dm, 'fecha_asignacion', None) or None,
                    fecha_hasta=None,
                    observaciones='',
                )
                created += 1
            except Exception:
                continue

    if DocenteAsignatura is not None:
        for da in DocenteAsignatura.objects.all():
            docente_id = getattr(da, 'docente_id', getattr(da, 'docente', None))
            asignatura_id = getattr(da, 'asignatura_id', getattr(da, 'asignatura', None))
            if not docente_id or not asignatura_id:
                continue
            exists = Habilitacion.objects.filter(
                docente_id=docente_id,
                asignatura_id=asignatura_id,
                nivel='ASIGNATURA',
                activo=True,
            ).exists()
            if exists:
                continue
            try:
                Habilitacion.objects.create(
                    docente_id=docente_id,
                    nivel='ASIGNATURA',
                    modulo_id=None,
                    asignatura_id=asignatura_id,
                    activo=getattr(da, 'activo', True),
                    fecha_desde=getattr(da, 'fecha_asignacion', None) or None,
                    fecha_hasta=None,
                    observaciones='',
                )
                created += 1
            except Exception:
                continue


def reverse(apps, schema_editor):
    # Por seguridad NO borramos los registros creados en la migración automática.
    return


class Migration(migrations.Migration):

    dependencies = [
        ('docentes', '0002_habilitaciondocente_alter_disponibilidad_options_and_more'),
        ('programa', '0001_initial'),
        ('competencia', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=reverse),
    ]
