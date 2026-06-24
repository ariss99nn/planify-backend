"""Re-exports for test factories.

Historically the project kept factory helpers in `aulas.tests.__init__`.
Some tests import `aulas.tests.factories`, so re-export the helpers here
to keep compatibility.
"""

from . import make_bloque, make_equipamiento, make_aula  # noqa: F401
