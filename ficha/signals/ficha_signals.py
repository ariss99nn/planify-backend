# ficha/signals/ficha_signals.py
# FIX: import correcto (sin prefijo back.) a nivel de módulo, sin import diferido.
from django.db.models.signals import pre_save
from django.dispatch import receiver
from ficha.models.ficha_historial_etapa_model import HistorialEtapa


@receiver(pre_save, sender='ficha.Ficha')
def registrar_cambio_etapa(sender, instance, **kwargs):
    """
    Crea un HistorialEtapa cada vez que Ficha.etapa cambia.
    Se captura en pre_save para poder leer el valor anterior desde la BD.
    El trimestre grabado es el del estado ANTERIOR al cambio.
    """
    if not instance.pk:
        return  # Instancia nueva — nada que comparar

    try:
        anterior = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    # Solo registrar si la ETAPA cambió (cambios de trimestre u otros campos se ignoran)
    if anterior.etapa == instance.etapa:
        return

    HistorialEtapa.objects.create(
        ficha          = instance,
        etapa_anterior = anterior.etapa,
        etapa_nueva    = instance.etapa,
        trimestre      = anterior.trimestre,
        cambiado_por   = getattr(instance, '_cambiado_por', None),
    )