from rest_framework import viewsets, response
from django.contrib.auth.models import User
from django.middleware.csrf import get_token

from .serializers import UserSerializer


class CurrentUserView(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        if not request.user.is_authenticated:
            return response.Response({}, 401)
        return response.Response(UserSerializer(request.user).data)


class CsrfTokenView(viewsets.GenericViewSet):

    def list(self, request):
        csrf_token = get_token(request)

        return response.Response({'csrf_token': csrf_token})
