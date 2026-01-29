from django.db import models
from django.conf import settings
from appointments.models import Appointment

class ChatRoom(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='chat_room'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chat: {self.appointment.patient.username} - {self.appointment.doctor.username}"

class Message(models.Model):
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
