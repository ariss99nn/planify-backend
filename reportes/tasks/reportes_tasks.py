# reportes/tasks/reportes_tasks.py
from celery import shared_task
from django.core.files.base import ContentFile


@shared_task(bind=True)
def generar_reporte(self, reporte_id: int):
    """
    Genera PDF y Excel para un ReporteGenerado ya creado en BD.
    El registro se crea en la vista (estado=PENDIENTE) antes de
    despachar esta tarea; aquí solo se procesa y se adjuntan archivos.
    """
    from reportes.models.reporte_generado_model import ReporteGenerado
    from reportes.services.reporte_factory import ReporteFactory

    try:
        reporte = ReporteGenerado.objects.get(pk=reporte_id)
    except ReporteGenerado.DoesNotExist:
        return

    reporte.estado = ReporteGenerado.EstadoReporte.PROCESANDO
    reporte.save(update_fields=['estado', 'updated_at'])

    try:
        generador = ReporteFactory.crear(reporte.tipo, reporte.filtros)

        pdf_bytes = generador.generar_pdf()
        excel_bytes = generador.generar_excel()

        nombre_base = f"{reporte.tipo.lower()}_{reporte.pk}"
        reporte.archivo_pdf.save(
            f"{nombre_base}.pdf", ContentFile(pdf_bytes), save=False,
        )
        reporte.archivo_excel.save(
            f"{nombre_base}.xlsx", ContentFile(excel_bytes), save=False,
        )
        reporte.estado = ReporteGenerado.EstadoReporte.LISTO
        reporte.error_mensaje = ''
        reporte.save(update_fields=[
            'estado', 'archivo_pdf', 'archivo_excel',
            'error_mensaje', 'updated_at',
        ])
    except Exception as exc:
        reporte.estado = ReporteGenerado.EstadoReporte.ERROR
        reporte.error_mensaje = str(exc)
        reporte.save(update_fields=['estado', 'error_mensaje', 'updated_at'])