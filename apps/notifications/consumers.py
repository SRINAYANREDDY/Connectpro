import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
            return
        self.user = self.scope['user']
        self.group_name = f'notifications_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({'type': 'init', 'unread_count': unread_count}))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'mark_read':
            await self.mark_all_read()
            await self.send(text_data=json.dumps({'type': 'marked_read'}))

    async def notification_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'notification_type': event['notification_type'],
            'sender': event['sender'],
            'sender_avatar': event['sender_avatar'],
            'unread_count': event['unread_count'],
        }))

    @database_sync_to_async
    def get_unread_count(self):
        return Notification.objects.filter(recipient=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_all_read(self):
        Notification.objects.filter(recipient=self.user, is_read=False).update(is_read=True)
