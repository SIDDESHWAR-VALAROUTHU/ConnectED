import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.me = self.scope["user"]
        self.other_username = self.scope["url_route"]["kwargs"]["username"]
        self.room_name = f"chat_{'_'.join(sorted([self.me.username, self.other_username]))}"

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        sender = self.me
        receiver = await sync_to_async(User.objects.get)(username=self.other_username)

        msg_obj = await sync_to_async(Message.objects.create)(
            sender=sender, receiver=receiver, content=message
        )

        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender.username,
                'is_new': True,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"]
        }))
