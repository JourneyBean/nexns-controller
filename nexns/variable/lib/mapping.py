import collections
from ..models import Variable
from .expression import RecordExpression
from .exceptions import ParseError


class UserVariablesMapping(collections.abc.Mapping):
    def __init__(self, user):
        self.queryset = Variable.objects.filter(user=user)

    def __getitem__(self, key):
        return self.queryset.get(name=key).text
    
    def __len__(self):
        len(self.queryset)

    def __iter__(self):
        return self.iter()
    
    def iter(self):
        for variable in self.queryset:
            yield variable.name
        return


def get_user_variables_dict(user) -> 'dict[str, RecordExpression]':
    """
    all {name: text} k-v pairs of a user
    """
    
    original = dict(UserVariablesMapping(user))

    need_process = original
    processed = {}

    while len(need_process):

        tmp = {}
        has_modification = False

        for key in need_process:

            print(key)

            try:
                # bootstraping variables using initialized variables
                data = RecordExpression(need_process[key], processed)
                processed[key] = data
                has_modification = True
            except Exception:
                tmp[key] = original[key]
        
        need_process = tmp

        # no further modifications
        if not has_modification:
            break

    if len(need_process):
        try:
            RecordExpression(need_process[list(need_process.keys())[0]], processed)
        except ParseError as e:
            raise e

    return processed
