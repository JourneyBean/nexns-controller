from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import viewsets, response
from nexns.name.models import Domain


class PublishView(viewsets.ViewSet):

    def retrieve(self, request, pk: str, format=None):

        domain = Domain.objects.get(id=pk)
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            'notification',
            {
                "type": "notify",
                "action": "domain-update",
                "domain": domain.id
            }
        )

        return response.Response({
            'message': "success"
        })
