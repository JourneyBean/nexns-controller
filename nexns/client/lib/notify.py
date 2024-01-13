from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def notify_domain_update(domain_id: int):

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        'notification',
        {
            "type": "notify",
            "action": "domain-update",
            "domain": domain_id
        }
    )
