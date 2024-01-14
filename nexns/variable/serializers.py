from rest_framework import serializers
from .models import Variable


class VariableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Variable
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
        ]
