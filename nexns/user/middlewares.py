from django.http import JsonResponse
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
