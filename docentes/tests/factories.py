from docentes.models.docente_model import Docente
from users.tests.factories import make_user
from users.models.user import User


def make_docente_user(**kwargs):
    """User con rol=DOCENTE, listo para tener perfil Docente."""
    return make_user(rol=User.Rol.DOCENTE, **kwargs)


def make_docente(user=None, especialidad='Matemáticas', horas=20, estado=True, **kwargs):
    """Crea un Docente completo con su User asociado."""
    if user is None:
        user = make_docente_user()
    return Docente.objects.create(
        user=user,
        especialidad=especialidad,
        horas_max_semanales=horas,
        estado=estado,
        **kwargs,
    )


def make_docente_inactivo(**kwargs):
    return make_docente(estado=False, **kwargs)