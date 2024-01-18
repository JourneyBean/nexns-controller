import traceback
import re
from typing import TYPE_CHECKING
from ipaddress import IPv4Address, IPv6Address

from rest_framework.serializers import ValidationError
from nexns.variable.lib import (
    get_user_variables_dict, update_user_variables, 
    RecordExpression, ParseError
)

if TYPE_CHECKING:
    from .models import Domain, Zone, RRset, RecordData

class DomainPublishValidator:
    def __call__(self, domain: 'Domain'):

        user = domain.user

        # update user variables
        try:
            update_user_variables(user)
        except Exception as e:
            traceback.print_exc()
            raise ValidationError(f"Error updating variables: {e}")

        variables = get_user_variables_dict(user)

        # update record data
        for zone in domain.zones.all():
            for rrset in zone.rrsets.all():
                for record in rrset.records.all():
                    try:
                        record.val = str(RecordExpression(record.text, variables))
                    except ParseError as e:
                        raise ValidationError(f"zone: {zone.name}, rrset: {rrset.name}, {str(e)}")
                    record.save()


class DomainRecordValidator:
    def __call__(self, domain: 'Domain'):
        
        for zone in domain.zones.all():
            validator = RecordValueValidator(zone)

            for rrset in zone.rrsets.all():

                for record in rrset.records.all():
                    try:
                        validator(rrset, record)
                    except ValidationError as e:
                        raise ValidationError(f"at zone={zone.name}, subdomain={rrset.name}, type={rrset.type}, record={record.text} {e}")


class RecordValueValidator:
    def __init__(self, zone: 'Zone'):
        self.zone = zone

    def subdomain_exists(self, subdomain: str) -> bool:
        try:
            self.zone.rrsets.get(name=subdomain)
            return True
        except Exception:
            return False
        
    def validate_subdomain_exists(self, subdomain: str):
        if not self.subdomain_exists(subdomain):
            raise ValidationError('Subdomain not found in zone.')
    
    def __call__(self, rrset: 'RRset', record: 'RecordData'):

        dns_type = rrset.type
        val = record.val

        if dns_type == 'A':
            try:
                IPv4Address(val)
            except Exception as e:
                raise ValidationError('Not a valid IPv4 address.')
            
        elif dns_type == 'AAAA':
            try:
                IPv6Address(val)
            except Exception as e:
                raise ValidationError('Not a valid IPv6 address.')
            
        elif dns_type == 'CNAME':
            if not val.endswith('.'):
                self.validate_subdomain_exists(val)

        elif dns_type == 'NS':
            if not val.endswith('.'):
                self.validate_subdomain_exists(val)
            
        elif dns_type == 'MX':
            result = re.findall(r'(\d+) +(\S+)', val)
            if len(result) != 1:
                raise ValidationError('Record format error')
            if not result[0][1].endswith('.'):
                self.validate_subdomain_exists(result[0][1])
