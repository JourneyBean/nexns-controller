from rest_framework import viewsets, response, decorators

from .models import Variable
from .serializers import VariableSerializer
from .lib import update_user_variables


class VariableView(viewsets.ModelViewSet):

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer

    def get_queryset(self):
        queryset = self.queryset

        user = self.request.query_params.get('user', None)

        if user is not None:
            queryset = self.queryset.filter(user=user)

        return queryset
    
    @decorators.action(detail=False, methods=['post'])
    def apply(self, request):
        user = self.request.query_params.get('user', None)
        update_user_variables(user)
        return response.Response(
            VariableSerializer(Variable.objects.filter(user=user), many=True).data
        )
