from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.decorators import decorator_from_middleware

from .lib.scope import ApiKeyScope
from .models import UserApiKey


class ApiKeyAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_apikey_auth = False
        secret = request.headers.get('x-apikey', None)
        
        if secret is None:
            response = self.get_response(request)
            return response

        try:
            key_object = UserApiKey.objects.get(secret=secret)
            request.user = key_object.user
            request.apikey_scope = ApiKeyScope.from_dict(key_object.scope)
            request.is_apikey_auth = True
        except UserApiKey.DoesNotExist:
            return JsonResponse({'error': 'Invalid API Key'}, status=401)            

        response = self.get_response(request)
        return response
    

class CsrfExemptApiKeyMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if (getattr(callback, 'csrf_exempt', False) or 
            getattr(request, 'is_apikey_auth', False)):
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)


def csrf_exempt_apikey(view_func):
    # use this as decorator if needed
    return decorator_from_middleware(CsrfExemptApiKeyMiddleware)(view_func)
