from rest_framework import viewsets, views, response
from .models import Domain, Zone, RRset, RecordData
from .serializers import DomainSerializer, ZoneSerializer, RRsetSerializer, RecordDataSerializer


def bulk_update(original_set, data, serializer_class, on_save_fn=None):
    
    
    need_delete_set = original_set.exclude(id__in=[o["id"] for o in data])
    need_create_set = []
    need_updated_set = []

    # validate
    for d in data:
        if d["id"] > 0:
            serializer = serializer_class(original_set.get(id=d["id"]), data=d)
            if not serializer.is_valid():
                raise ValueError(f'data not valid: {d}, {serializer.errors}')
            need_updated_set.append((serializer, d))
            continue

        del d["id"]
        serializer = serializer_class(data=d)
        if not serializer.is_valid():
            raise ValueError(f'data not valid: {d}, {serializer.errors}')
        need_create_set.append((serializer, d))

    # perform change
    need_delete_set.delete()
    for s in need_create_set:
        instance = s[0].save()
        if on_save_fn:
            on_save_fn(s[0], s[1], instance)
    for s in need_updated_set:
        instance = s[0].save()
        if on_save_fn:
            on_save_fn(s[1], s[1], instance)


class DomainView(viewsets.ModelViewSet):

    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

    def get_queryset(self):
        queryset = self.queryset

        user = self.request.query_params.get('user', None)

        if user is not None:
            queryset = self.queryset.filter(user=user)

        return queryset
    

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