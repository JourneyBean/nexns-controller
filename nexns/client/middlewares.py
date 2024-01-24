from django.http import JsonResponse
from .models import Client


class ClientAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_id = request.headers.get('x-client-id', None)
        client_secret = request.headers.get('x-client-secret', None)

        if client_id is None and client_secret is None:
            response = self.get_response(request)
            return response

        try:
            client = Client.objects.get(uuid=client_id)
            if not client_secret or client_secret != client.secret:
                return JsonResponse({'error': 'Invalid client.'}, status=401)
            request.client = client
        except Client.DoesNotExist:
            return JsonResponse({'error': 'Invalid client'}, status=401)            

        response = self.get_response(request)
        return response
