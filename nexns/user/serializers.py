from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'is_superuser',
            'is_active',
            'date_joined',
            'last_login',
        )
        read_only_fields = (
            'id',
            'username',
            'email',
            'is_superuser',
            'is_active',
            'date_joined',
            'last_login',
        )
