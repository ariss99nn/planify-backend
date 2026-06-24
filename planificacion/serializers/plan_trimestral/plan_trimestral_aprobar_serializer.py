# planificacion/serializers/plan_trimestral/plan_trimestral_aprobar_serializer.py
import logging

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from planificacion.models.plan_trimestral_model import PlanTrimestral

logger = logging.getLogger(__name__)

TRANSICIONES_VALIDAS = {
    PlanTrimestral.EstadoPlan.BORRADOR:     [PlanTrimestral.EstadoPlan.EN_REVISION],
    PlanTrimestral.EstadoPlan.EN_REVISION:  [
        PlanTrimestral.EstadoPlan.APROBADO,
        PlanTrimestral.EstadoPlan.RECHAZADO,
    ],
    PlanTrimestral.EstadoPlan.APROBADO:     [PlanTrimestral.EstadoPlan.EN_EJECUCION],
    PlanTrimestral.EstadoPlan.EN_EJECUCION: [PlanTrimestral.EstadoPlan.CERRADO],
    PlanTrimestral.EstadoPlan.RECHAZADO:    [PlanTrimestral.EstadoPlan.BORRADOR],
    PlanTrimestral.EstadoPlan.CERRADO:      [],
}


class PlanTrimestralCambiarEstadoSerializer(serializers.ModelSerializer):
    """
    Gestiona transiciones de estado del plan trimestral.

    CORRECCIÓN Bug #10:
    - La transición BORRADOR → EN_REVISION ahora notifica por email
      a los coordinadores y administrativos activos.
    - La transición APROBADO → EN_EJECUCION notifica a todos los
      docentes asignados en ítems del plan.
    - APROBADO → guarda aprobado_por y fecha_aprobacion.
    - EN_REVISION → RECHAZADO requiere motivo_rechazo.
    Todas las notificaciones se disparan con transaction.on_commit()
    para garantizar que el email solo se envía si la transacción
    se confirma exitosamente.
    """

    class Meta:
        model  = PlanTrimestral
        fields = ['estado', 'motivo_rechazo']

    def validate(self, data):
        estado_nuevo  = data.get('estado')
        estado_actual = self.instance.estado
        transiciones  = TRANSICIONES_VALIDAS.get(estado_actual, [])

        if estado_nuevo not in transiciones:
            raise serializers.ValidationError({
                'estado': (
                    f'No se puede pasar de "{estado_actual}" a "{estado_nuevo}". '
                    f'Transiciones válidas: {transiciones or "ninguna"}.'
                )
            })

        if estado_nuevo == PlanTrimestral.EstadoPlan.APROBADO:
            if not self.instance.items.exists():
                raise serializers.ValidationError(
                    'No se puede aprobar un plan sin ítems.'
                )

        if estado_nuevo == PlanTrimestral.EstadoPlan.RECHAZADO:
            if not data.get('motivo_rechazo'):
                raise serializers.ValidationError({
                    'motivo_rechazo': 'Obligatorio al rechazar un plan.'
                })

        return data

    def update(self, instance, validated_data):
        estado_nuevo = validated_data['estado']
        request      = self.context.get('request')

        instance.estado = estado_nuevo
        update_fields   = ['estado']

        # ── Campos adicionales por transición ─────────────────────────────
        if estado_nuevo == PlanTrimestral.EstadoPlan.APROBADO:
            instance.aprobado_por     = request.user if request else None
            instance.fecha_aprobacion = timezone.now()
            update_fields += ['aprobado_por', 'fecha_aprobacion']

        elif estado_nuevo == PlanTrimestral.EstadoPlan.RECHAZADO:
            instance.motivo_rechazo = validated_data.get('motivo_rechazo', '')
            update_fields.append('motivo_rechazo')

        instance.save(update_fields=update_fields)

        # ── Bug #10 RESUELTO: notificaciones por transición ───────────────
        # transaction.on_commit garantiza que el email solo se envía
        # si la transacción de guardado termina exitosamente.

        if estado_nuevo == PlanTrimestral.EstadoPlan.EN_REVISION:
            # Notificar a coordinadores y administrativos
            self._notificar_en_revision(instance)

        elif estado_nuevo == PlanTrimestral.EstadoPlan.EN_EJECUCION:
            # Notificar a todos los docentes asignados en el plan
            self._notificar_en_ejecucion(instance)

        elif estado_nuevo == PlanTrimestral.EstadoPlan.RECHAZADO:
            # Notificar al creador / docentes que el plan fue rechazado
            self._notificar_rechazado(instance)

        elif estado_nuevo == PlanTrimestral.EstadoPlan.APROBADO:
            # Notificar al equipo que el plan quedó aprobado y listo para generar horario
            self._notificar_aprobado(instance)

        return instance

    # ── Helpers de notificación ───────────────────────────────────────────

    @staticmethod
    def _notificar_en_revision(plan: PlanTrimestral) -> None:
        """Notifica a gestores que hay un plan esperando revisión."""
        from users.models.user import User

        gestores_emails = list(
            User.objects.filter(
                rol__in=[User.Rol.COORDINADOR, User.Rol.ADMINISTRATIVO],
                is_active=True,
            ).values_list('email', flat=True)
        )
        if not gestores_emails:
            return

        transaction.on_commit(lambda: _send_plan_en_revision(gestores_emails, plan))
        logger.info(
            'Plan %s pasó a EN_REVISION — notificando %d gestores.',
            plan, len(gestores_emails),
        )

    @staticmethod
    def _notificar_en_ejecucion(plan: PlanTrimestral) -> None:
        """Notifica a los docentes del plan que este ha iniciado ejecución."""
        docentes_emails = list(
            plan.items.filter(docente__isnull=False)
            .values_list('docente__user__email', flat=True)
            .distinct()
        )
        if not docentes_emails:
            return

        transaction.on_commit(lambda: _send_plan_en_ejecucion(docentes_emails, plan))
        logger.info(
            'Plan %s pasó a EN_EJECUCION — notificando %d docentes.',
            plan, len(docentes_emails),
        )

    @staticmethod
    def _notificar_rechazado(plan: PlanTrimestral) -> None:
        """Notifica a los docentes del plan que fue rechazado."""
        docentes_emails = list(
            plan.items.filter(docente__isnull=False)
            .values_list('docente__user__email', flat=True)
            .distinct()
        )
        if not docentes_emails:
            return

        transaction.on_commit(lambda: _send_plan_rechazado(docentes_emails, plan))
        logger.info('Plan %s RECHAZADO — notificando %d docentes.', plan, len(docentes_emails))

    @staticmethod
    def _notificar_aprobado(plan: PlanTrimestral) -> None:
        """Notifica a coordinadores que el plan fue aprobado."""
        from users.models.user import User

        coordinadores_emails = list(
            User.objects.filter(
                rol=User.Rol.COORDINADOR,
                is_active=True,
            ).values_list('email', flat=True)
        )
        if not coordinadores_emails:
            return

        transaction.on_commit(lambda: _send_plan_aprobado(coordinadores_emails, plan))
        logger.info('Plan %s APROBADO — notificando coordinadores.', plan)


# ── Funciones de envío de email ───────────────────────────────────────────────
# Se separan del serializer para poder testearlas de forma aislada
# y para que transaction.on_commit() capture el closure correctamente.

def _send_plan_en_revision(emails: list, plan: PlanTrimestral) -> None:
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(
            subject=f'[SENA] Plan trimestre {plan.trimestre} enviado a revisión — {plan.ficha}',
            message=(
                f'El plan trimestral del trimestre {plan.trimestre} '
                f'de la ficha {plan.ficha.codigo_ficha} '
                f'({plan.ficha.version.programa.nombre}) '
                f'ha sido enviado a revisión y está pendiente de aprobación.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True,
        )
    except Exception:
        logger.exception('Error enviando email plan EN_REVISION plan_id=%s', plan.pk)


def _send_plan_en_ejecucion(emails: list, plan: PlanTrimestral) -> None:
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(
            subject=f'[SENA] Tu plan del trimestre {plan.trimestre} está en ejecución — {plan.ficha}',
            message=(
                f'El plan trimestral del trimestre {plan.trimestre} '
                f'de la ficha {plan.ficha.codigo_ficha} ha sido aprobado '
                f'e inicia su ejecución. '
                f'Fecha de inicio: {plan.fecha_inicio}. '
                f'Consulta tu horario en el sistema.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True,
        )
    except Exception:
        logger.exception('Error enviando email plan EN_EJECUCION plan_id=%s', plan.pk)


def _send_plan_rechazado(emails: list, plan: PlanTrimestral) -> None:
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(
            subject=f'[SENA] Plan trimestre {plan.trimestre} rechazado — {plan.ficha}',
            message=(
                f'El plan trimestral del trimestre {plan.trimestre} '
                f'de la ficha {plan.ficha.codigo_ficha} fue rechazado.\n\n'
                f'Motivo: {plan.motivo_rechazo or "Sin especificar"}.\n\n'
                f'Por favor corrígelo y vuelve a enviarlo a revisión.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True,
        )
    except Exception:
        logger.exception('Error enviando email plan RECHAZADO plan_id=%s', plan.pk)


def _send_plan_aprobado(emails: list, plan: PlanTrimestral) -> None:
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(
            subject=f'[SENA] Plan trimestre {plan.trimestre} aprobado — {plan.ficha}',
            message=(
                f'El plan trimestral del trimestre {plan.trimestre} '
                f'de la ficha {plan.ficha.codigo_ficha} ha sido aprobado. '
                f'Ya puede proceder a generar el horario automático desde el sistema.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True,
        )
    except Exception:
        logger.exception('Error enviando email plan APROBADO plan_id=%s', plan.pk)