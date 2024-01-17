from rest_framework import serializers
from .models import Domain, Zone, RRset, RecordData


class DomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Domain
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
        ]
    
    def to_internal_value(self, data):
        # Access the current user from the context
        # user = self.context['request'].user 

        # Update the "user" field with the current user's ID
        data['user'] = 1

        return super().to_internal_value(data)
        

class ZoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Zone
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
        ]
        ordering = ['order']


class RRsetSerializer(serializers.ModelSerializer):

    class Meta:
        model = RRset
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
        ]
        ordering = ['order']


class RecordDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecordData
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
        ]
        ordering = ['order']
