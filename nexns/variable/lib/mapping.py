import collections
from ..models import Variable
from .expression import RecordExpression
from .exceptions import ParseError


class UserVariablesMapping(collections.abc.Mapping):
    def __init__(self, user):
        self.queryset = Variable.objects.filter(user=user)

    def __getitem__(self, key):
        return self.queryset.get(name=key).val
    
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
    
    return dict(UserVariablesMapping(user))


def update_user_variables(user) -> 'dict[str, RecordExpression]':

    queryset = Variable.objects.filter(user=user)

    need_process = queryset

    while len(need_process):

        tmp = {}
        has_modification = False
        processed = {}

        for obj in need_process:
            
            try:
                # bootstraping variables using initialized variables
                data = RecordExpression(obj.text, processed)

                obj.val = str(data)
                obj.save()

                processed[obj.name] = data
                has_modification = True

            except Exception:
                tmp.append(obj)
        
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
