from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.conf import settings


class EmailVerification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_verifications',
    )

    code = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    is_used = models.BooleanField(default=False)       # Invalidado (expiró o fue reemplazado)
    is_verified = models.BooleanField(default=False)   # Usado exitosamente por el usuario
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Verificación de correo'
        verbose_name_plural = 'Verificaciones de correo'
        indexes = [
            models.Index(fields=['user', 'code']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_used']),
        ]

    def __str__(self):
        return f"Verificación de {self.user.email} — {'usada' if self.is_used else 'pendiente'}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Un código es válido si no fue usado ni expiró."""
        return not self.is_used and not self.is_expired()

    def mark_as_verified(self):
        """Marca el código como verificado exitosamente."""
        self.is_used = True
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=['is_used', 'is_verified', 'verified_at'])

    @staticmethod
    def get_expiration_time(minutes=10):
        return timezone.now() + timedelta(minutes=minutes)

    @classmethod
    def invalidate_previous_codes(cls, user):
        """Invalida todos los códigos pendientes del usuario (sin marcarlos como verificados)."""
        cls.objects.filter(user=user, is_used=False).update(is_used=True)