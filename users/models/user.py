from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from users.validators import validate_imagen


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('El email debe ser proporcionado.')

        email = self.normalize_email(email)
        estado = extra_fields.pop('estado', None)
        if estado is not None:
            extra_fields['is_active'] = estado

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
    )

    class Rol(models.TextChoices):
        ADMINISTRATIVO = 'ADMINISTRATIVO', 'Administrativo'
        COORDINADOR = 'COORDINADOR', 'Coordinación'
        DOCENTE = 'DOCENTE', 'Docente'
        ESTUDIANTE = 'ESTUDIANTE', 'Estudiante'

    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)

    email = models.EmailField(unique=True)
    email_verificado = models.BooleanField(default=False)

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.ESTUDIANTE,
    )

    # El usuario se activa solo tras verificar su correo
    is_active = models.BooleanField(default=False)

    imagen = models.ImageField(
        upload_to='usuarios/',
        blank=True,
        null=True,
        validators=[validate_imagen],
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.get_rol_display()}"

    @property
    def estado(self):
        return self.is_active

    @estado.setter
    def estado(self, value):
        self.is_active = value

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()

    @property
    def es_estudiante(self):
        return self.rol == self.Rol.ESTUDIANTE

    @property
    def es_docente(self):
        return self.rol == self.Rol.DOCENTE

    @property
    def es_administrativo(self):
        return self.rol == self.Rol.ADMINISTRATIVO

    @property
    def es_coordinador(self):
        return self.rol == self.Rol.COORDINADOR

    @property
    def puede_gestionar_usuarios(self):
        """Shortcut para saber si el usuario tiene rol de gestión."""
        return self.rol in (self.Rol.ADMINISTRATIVO, self.Rol.COORDINADOR)

    @property
    def imagen_url(self):
        if self.imagen:
            return self.imagen.url
        return None

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['apellido', 'nombre']
        permissions = [
            # Visualización
            ("ver_estudiantes", "Puede ver estudiantes"),
            ("ver_docentes", "Puede ver docentes"),
            ("ver_administrativos", "Puede ver administrativos"),
            ("ver_coordinadores", "Puede ver coordinadores"),
            # Horarios (permiso externo relacionado)
            ("ver_horarios", "Puede ver horarios"),
            # CRUD de usuarios
            ("crear_usuarios", "Puede crear usuarios"),
            ("editar_usuarios", "Puede editar usuarios"),
            ("desactivar_usuarios", "Puede desactivar usuarios"),
            ("eliminar_usuarios", "Puede eliminar usuarios"),
            # Permisos y roles
            ("gestionar_permisos", "Puede gestionar permisos"),
            ("gestionar_roles", "Puede gestionar roles"),
        ]