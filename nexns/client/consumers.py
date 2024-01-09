import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Client


class ClientAuthenticationMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # 从请求头中获取 X-CLIENT-ID 和 X-CLIENT-SECRET
        client_id = next((value for key, value in scope.get('headers', {}) if key == b'x-client-id'), b'').decode('utf-8')
        client_secret = next((value for key, value in scope.get('headers', {}) if key == b'x-client-secret'), b'').decode('utf-8')

        # 验证客户端信息
        client = await self.authenticate(client_id, client_secret)

        # 将验证结果存储在 scope 中
        scope['client'] = client

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def authenticate(self, client_id, client_secret):
        # 根据 client_id 和 client_secret 从数据库中查找用户
        try:
            client = Client.objects.get(uuid=client_id, secret=client_secret)
            return client
        except Exception as e:
            print(e)
            return None


class ClientNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope.get('client', None):
            await self.channel_layer.group_add(
                'notification', self.channel_name
            )
            await self.accept()
        else:
            await self.close(403)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    async def notify(self, event):
        await self.send(text_data=json.dumps(event))
    