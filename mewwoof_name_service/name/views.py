from rest_framework import viewsets, response
from .models import Domain, Zone, Record
from .serializers import DomainSerializer, ZoneSerializer, RecordSerializer


class DomainView(viewsets.ModelViewSet):

    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    

class ZoneView(viewsets.ModelViewSet):

    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    

class RecordView(viewsets.ModelViewSet):

    queryset = Record.objects.all()
    serializer_class = RecordSerializer


class DumpView(viewsets.ViewSet):

    def retrieve(self, request, pk: str, format=None):

        if str(pk).isnumeric():
            domain = Domain.objects.get(id=pk)
        else:
            domain = Domain.objects.get(domain=pk)
        domain_serialized = DomainSerializer(domain).data
        
        zones = domain.zones.all().order_by('order')
        zones_serialized = []
        for zone in zones:

            zone_serialized = ZoneSerializer(zone).data

            records = zone.records.all().order_by('order')
            records_serialized = RecordSerializer(records, many=True).data
            zone_serialized['records'] = records_serialized

            zones_serialized.append(zone_serialized)

        return response.Response({
            'domain': domain_serialized,
            'zones': zones_serialized,
        })
