import logging
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def _get_client_ip(request) -> str:
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # XFF puede ser "client_ip, proxy1_ip, proxy2_ip"
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


RATE_LIMITS = {
    'COORDINADOR':   300,
    'ADMINISTRATIVO': 200,
    'DOCENTE':       100,
    'ESTUDIANTE':     60,
    'anonymous':      30,
}
WINDOW_SECONDS = 60


class RolBasedRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._is_rate_limited(request):
            return JsonResponse(
                {
                    'error': 'Too Many Requests',
                    'detail': 'Has superado el límite de solicitudes. Intenta de nuevo en un momento.',
                },
                status=429,
            )
        return self.get_response(request)

    def _is_rate_limited(self, request) -> bool:
        ip   = _get_client_ip(request)
        role = self._get_role(request)
        limit = RATE_LIMITS.get(role, RATE_LIMITS['anonymous'])

        cache_key = f'rl:{role}:{ip}'
        count = cache.get(cache_key, 0)

        if count >= limit:
            logger.warning(
                'Rate limit superado — ip=%s rol=%s count=%d limit=%d',
                ip, role, count, limit,
            )
            return True

        # Incrementar con TTL; si la clave no existía, crearla con el TTL completo.
        try:
            cache.incr(cache_key)
        except ValueError:
            # La clave no existía (cache.incr falla si no existe en algunos backends)
            cache.set(cache_key, 1, WINDOW_SECONDS)

        return False

    @staticmethod
    def _get_role(request) -> str:
        if request.user and request.user.is_authenticated:
            return getattr(request.user, 'rol', 'anonymous')
        return 'anonymous'
