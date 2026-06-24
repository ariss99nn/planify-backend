import logging
import time

logger = logging.getLogger('audit')

METODOS_AUDITABLES = {'POST', 'PATCH', 'PUT', 'DELETE'}


class AuditMiddleware:
    """
    Registra operaciones de escritura con usuario, endpoint, duración y status.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        inicio = time.time()
        response = self.get_response(request)
        duracion = round((time.time() - inicio) * 1000, 2)

        if request.method in METODOS_AUDITABLES:
            usuario = 'anónimo'
            if hasattr(request, 'user') and request.user.is_authenticated:
                usuario = request.user.email

            logger.info(
                "AUDIT | %s | %s | %s | %sms | %s",
                request.method,
                request.path,
                usuario,
                duracion,
                response.status_code,
            )

        return response