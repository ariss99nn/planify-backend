import logging
from django.core.management.base import BaseCommand, CommandError
from users.models.user import User
from users.services.role_service import sync_user_group

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        'Restaura el rol COORDINADOR a un usuario existente y lo activa. '
        'Usar cuando no quede ningún coordinador activo en el sistema.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email del usuario a restaurar como coordinador.',
        )

    def handle(self, *args, **options):
        email = options['email'].strip().lower()

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise CommandError(f"No existe ningún usuario con el email '{email}'.")

        if user.rol == User.Rol.COORDINADOR and user.is_active:
            self.stdout.write(
                self.style.WARNING(
                    f"'{email}' ya es COORDINADOR activo. No se realizaron cambios."
                )
            )
            return

        user.rol = User.Rol.COORDINADOR
        user.is_active = True
        user.save(update_fields=['rol', 'is_active'])

        sync_user_group(user)

        logger.info("Coordinador restaurado: %s", email)

        self.stdout.write(
            self.style.SUCCESS(f"'{email}' ahora es COORDINADOR activo.")
        )