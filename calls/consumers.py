import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from appointments.models import Appointment

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_token = self.scope['url_route']['kwargs']['token']
        self.room_group_name = f'video_call_{self.room_token}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.scope['user'].id if self.scope['user'].is_authenticated else None
            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.scope['user'].id if self.scope['user'].is_authenticated else None
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        # Forward WebRTC signaling messages to other participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_signal',
                'message': data,
                'sender_channel': self.channel_name
            }
        )

    async def webrtc_signal(self, event):
        # Don't send message back to sender
        if event['sender_channel'] != self.channel_name:
            await self.send(text_data=json.dumps(event['message']))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id']
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id']
        }))