from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone


class EmailChangeRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_change_requests',
    )

    new_email = models.EmailField()
    code = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Solicitud de cambio de correo'
        verbose_name_plural = 'Solicitudes de cambio de correo'
        indexes = [
            models.Index(fields=['user', 'is_used']),
            models.Index(fields=['new_email']),
        ]

    def __str__(self):
        return f"Cambio de correo de {self.user.email} → {self.new_email}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Un código es válido si no fue usado ni expiró."""
        return not self.is_used and not self.is_expired()

    def mark_as_used(self):
        self.is_used = True
        self.save(update_fields=['is_used'])

    @staticmethod
    def get_expiration_time(minutes=10):
        return timezone.now() + timedelta(minutes=minutes)

    @classmethod
    def invalidate_previous_requests(cls, user):
        """Invalida todas las solicitudes pendientes del usuario."""
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

    @classmethod
    def email_already_requested(cls, new_email):
        """
        Verifica si el nuevo correo ya tiene una solicitud activa
        de otro usuario. Útil para validar antes de crear la solicitud.
        """
        return cls.objects.filter(
            new_email=new_email,
            is_used=False,
            expires_at__gt=timezone.now(),
        ).exists()