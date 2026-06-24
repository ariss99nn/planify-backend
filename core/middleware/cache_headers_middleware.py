import hashlib
import logging

logger = logging.getLogger(__name__)


class ETagMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method != 'GET':
            return response

        if response.status_code != 200:
            return response

        last_modified = response.get('Last-Modified')
        if last_modified:
            etag = f'"{hashlib.sha256(last_modified.encode()).hexdigest()[:16]}"'
        else:
            try:
                content = response.content
                etag = f'"{hashlib.sha256(content).hexdigest()[:16]}"'
            except Exception:
                return response

        response['ETag'] = etag

        client_etag = request.META.get('HTTP_IF_NONE_MATCH', '')
        if client_etag and client_etag == etag:
            from django.http import HttpResponseNotModified
            not_modified = HttpResponseNotModified()
            not_modified['ETag'] = etag
            return not_modified

        return response
