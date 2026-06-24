import os
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.services.role_service import sync_user_group

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = "Crea el superusuario administrador inicial del sistema."

    def handle(self, *args, **kwargs):
        email = os.environ.get('SUPERUSER_EMAIL', 'admin@planify.com')
        password = os.environ.get('SUPERUSER_PASSWORD')        # ✅ nunca hardcodeado

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    "Define la variable de entorno SUPERUSER_PASSWORD antes de ejecutar este comando."
                )
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f"El superusuario '{email}' ya existe.")
            )
            return

        user = User(
            nombre='Administrador',
            apellido='Sistema',                                # ✅ añadido
            email=email,
            rol=User.Rol.ADMINISTRATIVO,
            is_active=True,
            email_verificado=True,                             # ✅ superuser ya verificado
            is_staff=True,
            is_superuser=True,
        )
        user.set_password(password)
        user.save()

        sync_user_group(user)

        logger.info("Superusuario creado: %s", email)
        self.stdout.write(
            self.style.SUCCESS(f"Superusuario creado correctamente: {email}")
        )