import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time messaging.
    Room group name: chat_<conversation_id>
    """

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = f"chat_{self.conversation_id}"
        self.user = self.scope["user"]

        # Reject unauthenticated connections
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        # Verify the user is a participant in this conversation
        is_participant = await self._is_participant()
        if not is_participant:
            await self.close()
            return

        # Join the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Notify others that this user came online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status",
                "user_id": self.user.id,
                "username": self.user.username,
                "status": "online",
            },
        )

    async def disconnect(self, code):
        if hasattr(self, "room_group_name"):
            # Notify group that user went offline
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_status",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "status": "offline",
                },
            )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming WebSocket message from the browser."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get("type", "message")

        if msg_type == "message":
            content = data.get("content", "").strip()
            if not content:
                return

            # Persist message to database
            msg = await self._save_message(content)
            if msg is None:
                return

            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message_id": msg["id"],
                    "sender_id": self.user.id,
                    "sender_username": self.user.username,
                    "sender_avatar": msg["sender_avatar"],
                    "content": content,
                    "created_at": msg["created_at"],
                },
            )

        elif msg_type == "typing":
            # Broadcast typing indicator (not stored)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_indicator",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "is_typing": data.get("is_typing", False),
                },
            )

        elif msg_type == "read":
            await self._mark_read()

    # ── Group message handlers ────────────────────────────────────────────────

    async def chat_message(self, event):
        """Send a chat message to the WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "message",
            "message_id": event["message_id"],
            "sender_id": event["sender_id"],
            "sender_username": event["sender_username"],
            "sender_avatar": event.get("sender_avatar", ""),
            "content": event["content"],
            "created_at": event["created_at"],
            "is_mine": event["sender_id"] == self.user.id,
        }))

    async def typing_indicator(self, event):
        """Forward typing indicator to the WebSocket (skip echo to sender)."""
        if event["user_id"] == self.user.id:
            return
        await self.send(text_data=json.dumps({
            "type": "typing",
            "user_id": event["user_id"],
            "username": event["username"],
            "is_typing": event["is_typing"],
        }))

    async def user_status(self, event):
        """Forward online/offline status updates."""
        if event["user_id"] == self.user.id:
            return
        await self.send(text_data=json.dumps({
            "type": "status",
            "user_id": event["user_id"],
            "username": event["username"],
            "status": event["status"],
        }))

    # ── DB helpers (run in thread pool via sync_to_async) ────────────────────

    @sync_to_async
    def _is_participant(self):
        from .models import Conversation
        return Conversation.objects.filter(
            pk=self.conversation_id,
            participants=self.user,
        ).exists()

    @sync_to_async
    def _save_message(self, content):
        from .models import Conversation, Message
        try:
            conv = Conversation.objects.get(pk=self.conversation_id)
        except Conversation.DoesNotExist:
            return None

        msg = Message.objects.create(
            conversation=conv,
            sender=self.user,
            content=content,
        )
        # Touch conversation.updated_at for inbox ordering
        conv.save()

        avatar = ""
        if hasattr(self.user, "avatar") and self.user.avatar:
            try:
                avatar = self.user.avatar.url
            except Exception:
                pass

        return {
            "id": msg.pk,
            "created_at": msg.created_at.strftime("%H:%M"),
            "sender_avatar": avatar,
        }

    @sync_to_async
    def _mark_read(self):
        from .models import Message
        Message.objects.filter(
            conversation_id=self.conversation_id,
            is_read=False,
        ).exclude(sender=self.user).update(is_read=True)
