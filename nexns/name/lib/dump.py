from typing import TYPE_CHECKING
from nexns.variable.lib import get_user_variables_dict, RecordExpression
from ..serializers import DomainSerializer, ZoneSerializer, RRsetSerializer, RecordDataSerializer

if TYPE_CHECKING:
    from ..models import Domain


def dump_domain(domain: 'Domain'):
    domain_data = DomainSerializer(domain).data
    
    variables = get_user_variables_dict(domain.user)

    zones = domain.zones.all().order_by('order')
    zones_data = []
    for zone in zones:

        zone_data = ZoneSerializer(zone).data

        rrsets = zone.rrsets.all().order_by('order')
        rrsets_data = []

        for rrset in rrsets:
            rrset_data = RRsetSerializer(rrset).data

            records_data = []
            for record_data in rrset.records.all():
                records_data.append({
                    'id': record_data.id,
                    'ttl': record_data.ttl,
                    'data': str(RecordExpression(record_data.data, variables)),
                    'order': record_data.order,
                })
            rrset_data['records'] = records_data

            rrsets_data.append(rrset_data)

        zone_data['rrsets'] = rrsets_data

        zones_data.append(zone_data)

    return {
        'domain': domain_data,
        'zones': zones_data
    }
