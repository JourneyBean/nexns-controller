from rest_framework import viewsets, views, response, decorators
from django.core.exceptions import SuspiciousOperation
from django.http import QueryDict

from nexns.client.lib import notify_domain_update
from nexns.client.permissions import IsAuthenticatedClient
from nexns.user.permissions import *

from .models import Domain, Zone, RRset, RecordData
from .serializers import DomainSerializer, ZoneSerializer, RRsetSerializer, RecordDataSerializer
from .validators import DomainPublishValidator, DomainRecordValidator
from .lib import bulk_update, dump_domain


class DomainView(viewsets.ModelViewSet):

    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [
        IsAuthenticatedUser | 
        IsAuthenticatedApiKey & ApiKeyDomainPermission
    ]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @decorators.action(methods=["POST"], detail=True)
    def apply(self, request, pk):
        """Inform servers to reload this domain"""

        domain: 'Domain' = self.get_object()

        # check domain
        DomainPublishValidator()(domain)
        DomainRecordValidator()(domain)

        notify_domain_update(domain.id)

        return response.Response({
            'message': "success"
        })
    
    @decorators.action(
        methods=["GET"],
        detail=False,
        url_path='dump',
        permission_classes=[IsAuthenticatedClient]
    )
    def dump_all(self, request):
        """Dump all domain data for client"""

        domains_data = []
        for domain in Domain.objects.all():
            domains_data.append(dump_domain(domain))

        return response.Response(domains_data)

    @decorators.action(
        methods=["GET"],
        detail=True,
        url_path='dump',
        permission_classes=[
            IsAuthenticatedClient |
            IsAuthenticatedUser | 
            IsAuthenticatedApiKey & ApiKeyDomainPermission
        ]
    )
    def dump(self, request, pk: str):
        """Dump one domain for client"""

        if str(pk).isnumeric():
            domain = Domain.objects.get(id=pk)
        else:
            domain = Domain.objects.get(domain=pk)
        
        domain_data = dump_domain(domain)

        return response.Response(domain_data)

    @decorators.action(
        methods=["GET"],
        detail=False,
        url_path='quick'
    )
    def quick_get(self, request):
        """Quickly get records via url query string"""

        domain, _, rrset = get_rrset(request)

        check_domain_user(request, domain)
        
        serializer = RecordDataSerializer(rrset.records, many=True)
        return response.Response(serializer.data)

    @decorators.action(
        methods=["POST", "PUT"],
        detail=False,
        url_path='quick'
    )
    def quick_update(self, request):
        """Quickly update records via url query string and multiform data"""

        request_data = request.data
        if isinstance(request_data, QueryDict):
            request_data = request_data.dict()
        domain, _, rrset = get_rrset(request)

        check_domain_user(request, domain)
        
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


class ZoneView(viewsets.ModelViewSet):

    queryset = Zone.objects.all().order_by('order')
    serializer_class = ZoneSerializer
    permission_classes = [
        IsAuthenticatedUser | 
        IsAuthenticatedApiKey & ApiKeyZonePermission
    ]

    def get_queryset(self):

        # limit to current user
        queryset = self.queryset.filter(domain__user=self.request.user)

        # url query: domain        
        domain = self.request.query_params.get('domain', None)
        if domain is not None:
            queryset = queryset.filter(domain=domain)

        return queryset

    @decorators.action(methods=["POST", "PUT"], detail=False, url_path='bulk-update')
    def bulk_update(self, request, *args, **kwargs):
        """Bulk update a zone, including rrsets and record data"""
        
        domain_id = self.request.query_params.get('domain', None)
        domain = Domain.objects.get(id=domain_id)

        check_domain_user(request, domain)

        zones = domain.zones.all()

        bulk_update(request, zones, request.data, ZoneSerializer)

        # 返回
        serializer = ZoneSerializer(domain.zones.all(), many=True)
        return response.Response(serializer.data)


class RRsetView(viewsets.ModelViewSet):

    queryset = RRset.objects.all().order_by('order')
    serializer_class = RRsetSerializer
    permission_classes = [
        IsAuthenticatedUser | 
        IsAuthenticatedApiKey & ApiKeyRRsetPermission
    ]

    def get_queryset(self):

        # limit to current user
        queryset = self.queryset.filter(zone__domain__user=self.request.user)

        # url query: zone
        zone = self.request.query_params.get('zone', None)
        if zone is not None:
            queryset = queryset.filter(zone=zone)

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

    @decorators.action(methods=["POST", "PUT"], detail=False, url_path='bulk-update')
    def bulk_update(self, request, *args, **kwargs):
        """Bulk update rrset, including nested record data"""

        zone_id = self.request.query_params.get('zone', None)
        zone = Zone.objects.get(id=zone_id)

        # limit to current user
        check_domain_user(request, zone.domain)

        rrsets = zone.rrsets.all()

        def on_rrset_save(serializer: RRsetSerializer, data: dict, instance: RRset):
            for record in data["records"]:
                record["rrset"] = instance.id
            bulk_update(request, instance.records.all(), data["records"], RecordDataSerializer)

        bulk_update(request, rrsets, request.data, RRsetSerializer, on_save_fn=on_rrset_save)

        return response.Response({'status': 'success'})


class RecordDataView(viewsets.ModelViewSet):

    queryset = RecordData.objects.all().order_by('order')
    serializer_class = RecordDataSerializer
    permission_classes = [
        IsAuthenticatedUser | 
        IsAuthenticatedApiKey & ApiKeyRecordPermission
    ]

    def get_queryset(self):

        # limit to current user
        queryset = self.queryset.filter(rrset__zone__domain__user=self.request.user)

        return queryset


def get_rrset(request) -> 'tuple[Domain, Zone, RRset]':
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
