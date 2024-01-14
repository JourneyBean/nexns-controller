from rest_framework import viewsets

from .models import Variable
from .serializers import VariableSerializer


class VariableView(viewsets.ModelViewSet):

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer

    def get_queryset(self):
        queryset = self.queryset

        user = self.request.query_params.get('user', None)

        if user is not None:
            queryset = self.queryset.filter(user=user)

        return queryset
