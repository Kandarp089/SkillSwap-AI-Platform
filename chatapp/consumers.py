import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message
from notifications.models import Notification

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        user = self.scope.get('user')
        if not user or user.is_anonymous or getattr(user, 'is_suspended', False):
            await self.close()
            return

        is_authorized = await self.check_room_authorization(user, self.room_name)
        if not is_authorized:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat_message')

            if message_type == 'chat_message':
                message_text = data.get('message', '').strip()
                receiver_username = data.get('receiver', '')

                if not message_text:
                    return

                sender = self.scope['user']
                receiver = await self.get_user(receiver_username)

                if receiver:
                    saved_msg = await self.save_message(sender, receiver, message_text)
                    await self.create_notification(receiver, sender, message_text)

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message_broadcast',
                            'message': message_text,
                            'sender': sender.username,
                            'receiver': receiver.username,
                            'timestamp': saved_msg.created_at.strftime("%I:%M %p"),
                            'message_id': saved_msg.id,
                        }
                    )
        except Exception as e:
            print(f"WebSocket error: {e}")

    async def chat_message_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'receiver': event['receiver'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))

    @database_sync_to_async
    def check_room_authorization(self, user, room_name):
        if user.is_staff or getattr(user, 'is_admin_or_staff', False):
            return True
        parts = [p.lower() for p in room_name.split('_')]
        return user.username.lower() in parts or str(user.id) in parts

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.filter(username__iexact=username).first()

    @database_sync_to_async
    def save_message(self, sender, receiver, text):
        return Message.objects.create(sender=sender, receiver=receiver, message=text)

    @database_sync_to_async
    def create_notification(self, receiver, sender, text):
        Notification.objects.create(
            user=receiver,
            sender=sender,
            notification_type='new_message',
            title=f"New message from {sender.username}",
            message=text[:100],
            link=f"/chat/?user={sender.username}"
        )
