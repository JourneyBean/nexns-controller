from rest_framework import viewsets, response, decorators

from nexns.name.lib.bulk_update import bulk_update
from nexns.user.permissions import *
from .models import Variable
from .serializers import VariableSerializer
from .lib import update_user_variables


class VariableView(viewsets.ModelViewSet):

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer
    permission_classes = [
        IsAuthenticatedUser |
        IsAuthenticatedApiKey & ApiKeyVariablePermission
    ]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    @decorators.action(detail=False, methods=['post'])
    def apply(self, request):
        user = request.user
        update_user_variables(user)
        return response.Response(
            VariableSerializer(Variable.objects.filter(user=user), many=True).data
        )

    @decorators.action(detail=False, methods=['PUT'])
    def bulk(self, request):
        queryset = self.get_queryset()
        bulk_update(queryset, request.data, self.serializer_class)

        serializer = self.serializer_class(self.get_queryset(), many=True)
        return response.Response(serializer.data)
    