from rest_framework import serializers
from .models import Domain, Zone, Record


class DomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Domain
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
        ]
        

class ZoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Zone
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
        ]
        ordering = ['order']


class RecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Record
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
        ]
        ordering = ['order']
