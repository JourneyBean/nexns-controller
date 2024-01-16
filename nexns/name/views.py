from rest_framework import viewsets, views, response, decorators
from django.core.exceptions import SuspiciousOperation
from django.http import QueryDict

from nexns.client.lib import notify_domain_update

from .models import Domain, Zone, RRset, RecordData
from .serializers import DomainSerializer, ZoneSerializer, RRsetSerializer, RecordDataSerializer
from .lib import bulk_update, dump_domain


class DomainView(viewsets.ModelViewSet):

    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

    def get_queryset(self):
        queryset = self.queryset

        user = self.request.query_params.get('user', None)

        if user is not None:
            queryset = self.queryset.filter(user=user)

        return queryset
    
    @decorators.action(methods=["POST"], detail=True)
    def apply(self, request, pk=None):
        """Inform servers to reload this domain"""

        domain: 'Domain' = self.get_object()

        notify_domain_update(domain.id)

        return response.Response({
            'message': "success"
        })


class ZoneView(viewsets.ModelViewSet):

    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer

    def get_queryset(self):
        queryset = self.queryset
        
        domain = self.request.query_params.get('domain', None)

        if domain is not None:
            queryset = self.queryset.filter(domain=domain)

        return queryset.order_by('order')
    

class ZoneUpdateView(views.APIView):
    def put(self, request, *args, **kwargs):
        domain_id = self.request.query_params.get('domain', None)
        domain = Domain.objects.get(id=domain_id)
        zones = domain.zones.all()

        bulk_update(zones, request.data, ZoneSerializer)

        # 返回
        serializer = ZoneSerializer(domain.zones.all(), many=True)
        return response.Response(serializer.data)


class RRsetView(viewsets.ModelViewSet):

    queryset = RRset.objects.all().order_by('order')
    serializer_class = RRsetSerializer

    def get_queryset(self):
        queryset = self.queryset

        zone = self.request.query_params.get('zone', None)

        if zone is not None:
            queryset = self.queryset.filter(zone=zone)

        return queryset
    
    def list(self, request, *args, **kwargs):
        detail = self.request.query_params.get('detail', None)

        if not detail:
            return super().list(request, *args, **kwargs)
        
        else:
            data = []
            rrsets = self.get_queryset()
            for rrset in rrsets:
                d = RRsetSerializer(rrset).data
                d["records"] = RecordDataSerializer(rrset.records, many=True).data
                data.append(d)
            return response.Response(data)


class RRsetUpdateView(views.APIView):
    def put(self, request, *args, **kwargs):
        zone_id = self.request.query_params.get('zone', None)
        zone = Zone.objects.get(id=zone_id)
        rrsets = zone.rrsets.all()

        def on_rrset_save(serializer: RRsetSerializer, data: dict, instance: RRset):
            for record in data["records"]:
                record["rrset"] = instance.id
            bulk_update(instance.records.all(), data["records"], RecordDataSerializer)

        bulk_update(rrsets, request.data, RRsetSerializer, on_save_fn=on_rrset_save)

        return response.Response({'status': 'success'})


class RecordDataView(viewsets.ModelViewSet):

    queryset = RecordData.objects.all()
    serializer_class = RecordDataSerializer


class DumpView(viewsets.ViewSet):

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
        
        domain_data = dump_domain(domain)

        return response.Response(domain_data)


def get_rrset(request, pk: str) -> 'tuple[Domain, Zone, RRset]':
    domain_id = request.query_params.get('domain_id', None)
    domain_name = request.query_params.get('domain_name', None)
    if domain_id is None and domain_name is None:
        raise SuspiciousOperation('Invalid query `domain_id` or `domain_name`')
    if domain_id is not None:
        domain = Domain.objects.get(id=domain_id)
    else:
        domain = Domain.objects.get(domain=domain_name)

    zone_id = request.query_params.get('zone_id', None)
    zone_name = request.query_params.get('zone_name', None)
    if zone_id is None and zone_name is None:
        raise SuspiciousOperation('Invalid query `zone_id` or `zone_name`.')
    if zone_id is not None:
        zone = domain.zones.get(id=zone_id)
    else:
        zone = domain.zones.get(name=zone_name)

    subdomain = request.query_params.get('subdomain', '')
    dns_type = request.query_params.get('type', None)
    if dns_type is None:
        raise SuspiciousOperation('Invalid query `type`.')
    
    
    rrset = zone.rrsets.get(name=subdomain, type=dns_type)
    return domain, zone, rrset
    

class RecordQuickUpdateView(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        _, _, rrset = get_rrset(request, pk)
        serializer = RecordDataSerializer(rrset.records, many=True)
        return response.Response(serializer.data)

    def update(self, request, pk=None):
        request_data = request.data
        if isinstance(request_data, QueryDict):
            request_data = request_data.dict()
        domain, zone, rrset = get_rrset(request, pk)
        
        records = rrset.records.all()

        if len(records) == 1 and records[0].data == request_data['data']:
            # exactly the same
            if records[0].ttl == int(request_data.get('ttl', records[0].ttl)):
                return response.Response({'status': 'success'}, 202)
            # update ttl
            else:
                records[0].ttl = int(request_data['ttl'])
                records[0].save()

                notify_domain_update(domain.id)
                return response.Response({'status': 'success'}, 200)
        
        # clear all records and add new record
        for r in records:
            r.delete()

        new_record = RecordData()
        new_record.rrset = rrset
        new_record.ttl = request_data.get('ttl', domain.ttl)
        new_record.data = request_data['data']
        new_record.order = 1
        new_record.save()

        notify_domain_update(domain.id)
        return response.Response({'status': 'success'}, 200)
