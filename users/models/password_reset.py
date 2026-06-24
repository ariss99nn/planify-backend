import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta

class PasswordReset(models.Model):
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_resets',
    )
    token      = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used       = models.BooleanField(default=False)

    class Meta:
        verbose_name        = 'Restablecimiento de contraseña'
        verbose_name_plural = 'Restablecimientos de contraseña'
        ordering            = ['-created_at']

    def __str__(self):
        return f'PasswordReset({self.user_id}, used={self.used})'

    @classmethod
    def get_expiration_time(cls) -> int:

        return getattr(settings, 'PASSWORD_RESET_EXPIRY_HOURS', 2)

    @property
    def is_expired(self) -> bool:
        hours   = self.get_expiration_time()
        expires = self.created_at + timedelta(hours=hours)
        return timezone.now() > expires

    @property
    def is_valid(self) -> bool:
        return not self.used and not self.is_expired
