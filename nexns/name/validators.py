import traceback
from rest_framework.serializers import ValidationError
from nexns.variable.lib import (
    get_user_variables_dict, update_user_variables, 
    RecordExpression, ParseError
)

class DomainPublishValidator:
    def __call__(self, domain):

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
