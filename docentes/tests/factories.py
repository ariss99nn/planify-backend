from docentes.models.docente_model import Docente
from users.tests.factories import make_user
from users.models.user import User


def make_docente_user(email=None, nombre=None, **kwargs):
    """
    User con rol=DOCENTE. Acepta email y nombre directamente.
    """
    return make_user(
        rol=User.Rol.DOCENTE,
        email=email,
        nombre=nombre,
        **kwargs,
    )


def make_docente(
    user=None,
    especialidad='Matemáticas',
    horas=20,
    estado=True,
    email=None,        # CORRECCIÓN: email se extrae para pasarlo al User
    nombre=None,       # CORRECCIÓN: nombre también
    **kwargs,
):
    """
    Crea un Docente completo con su User asociado.

    CORRECCIÓN: la versión original pasaba email y otros kwargs de User
    directamente a Docente.objects.create(), lo que causaba
    'unexpected keyword argument' porque Docente no tiene campo email.
    Ahora email y nombre se pasan a make_docente_user().
    """
    if user is None:
        user_kwargs = {}
        if email:
            user_kwargs['email'] = email
        if nombre:
            user_kwargs['nombre'] = nombre
        user = make_docente_user(**user_kwargs)

    return Docente.objects.create(
        user=user,
        especialidad=especialidad,
        horas_max_semanales=horas,
        estado=estado,
        **kwargs,
    )


def make_docente_inactivo(**kwargs):
    return make_docente(estado=False, **kwargs)