import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from appointments.models import Appointment

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.appointment_id = self.scope['url_route']['kwargs']['appointment_id']
        self.room_group_name = f'chat_{self.appointment_id}'
        self.user = self.scope['user']
        
        # Check if user is authenticated and has permission to access this chat
        if not self.user.is_authenticated:
            await self.close()
            return
            
        # Verify user has access to this appointment
        has_access = await self.check_user_access()
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Save message to database
        await self.save_message(message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'user_id': self.user.id,
                'timestamp': await self.get_current_timestamp()
            }
        )
    
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        user_id = event['user_id']
        timestamp = event['timestamp']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'user_id': user_id,
            'timestamp': timestamp
        }))
    
    @database_sync_to_async
    def check_user_access(self):
        try:
            appointment = Appointment.objects.get(id=self.appointment_id)
            # Only allow doctor and patient from this appointment to access chat
            return self.user == appointment.doctor or self.user == appointment.patient
        except Appointment.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, message):
        try:
            appointment = Appointment.objects.get(id=self.appointment_id)
            chat_room, created = ChatRoom.objects.get_or_create(appointment=appointment)
            Message.objects.create(
                chat_room=chat_room,
                sender=self.user,
                content=message
            )
        except Appointment.DoesNotExist:
            pass
    
    @database_sync_to_async
    def get_current_timestamp(self):
        from django.utils import timezone
        return timezone.now().strftime('%Y-%m-%d %H:%M:%S')