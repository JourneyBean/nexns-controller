from rest_framework import viewsets, response
from .models import Domain, Zone, RRset, RecordData
from .serializers import DomainSerializer, ZoneSerializer, RRsetSerializer, RecordDataSerializer


class DomainView(viewsets.ModelViewSet):

    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    

class ZoneView(viewsets.ModelViewSet):

    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    

class RRsetView(viewsets.ModelViewSet):

    queryset = RRset.objects.all()
    serializer_class = RRsetSerializer


class RecordDataView(viewsets.ModelViewSet):

    queryset = RecordData.objects.all()
    serializer_class = RecordDataSerializer


class DumpView(viewsets.ViewSet):

    def dump_domain(self, domain: 'Domain'):
        domain_data = DomainSerializer(domain).data
        
        zones = domain.zones.all().order_by('order')
        zones_data = []
        for zone in zones:

            zone_data = ZoneSerializer(zone).data

            rrsets = zone.rrsets.all().order_by('order')
            rrsets_data = []

            for rrset in rrsets:
                rrset_data = RRsetSerializer(rrset).data
                records_data = RecordDataSerializer(rrset.records, many=True).data
                rrset_data['records'] = records_data

                rrsets_data.append(rrset_data)

            zone_data['rrsets'] = rrsets_data

            zones_data.append(zone_data)

        return {
            'domain': domain_data,
            'zones': zones_data
        }

    def list(self, request):

        domains_data = []
        for domain in Domain.objects.all():
            domains_data.append(self.dump_domain(domain))

        return response.Response(domains_data)

    def retrieve(self, request, pk: str, format=None):

        if str(pk).isnumeric():
            domain = Domain.objects.get(id=pk)
        else:
            domain = Domain.objects.get(domain=pk)
        
        domain_data = self.dump_domain(domain)

        return response.Response(domain_data)
