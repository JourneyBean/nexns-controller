from rest_framework import serializers, validators
from .models import Variable


class VariableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Variable
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
        ]
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Variable.objects.all(),
                fields = ['user', 'name']
            )
        ]

    def to_internal_value(self, data):
        # Access the current user from the context
        user = self.context['request'].user.id

        # Update the "user" field with the current user's ID
        data['user'] = user

        return super().to_internal_value(data)
