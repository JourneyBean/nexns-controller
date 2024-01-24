from rest_framework import viewsets, response, decorators, permissions
from django.contrib.auth.models import User
from django.contrib.auth import hashers, password_validation
from .serializers import UserSerializer


class UserView(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class CurrentUserView(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        return response.Response(UserSerializer(request.user).data)
