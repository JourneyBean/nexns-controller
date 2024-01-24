from django.http import JsonResponse
from .models import UserApiKey


class ApiKeyAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        secret = request.headers.get('x-apikey', None)
        
        if secret is None:
            response = self.get_response(request)
            return response

        try:
            key_object = UserApiKey.objects.get(secret=secret)
            request.user = key_object.user
        except UserApiKey.DoesNotExist:
            return JsonResponse({'error': 'Invalid API Key'}, status=401)            

        response = self.get_response(request)
        return response
