from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = [
            'password',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
            'is_superuser',
            'date_joined',
        ]
