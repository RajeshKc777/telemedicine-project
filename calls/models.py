from django.db import models
from django.conf import settings
from appointments.models import Appointment
import random
import time

class VideoCall(models.Model):
    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        ACTIVE = "active", "Active"
        ENDED = "ended", "Ended"
        REJECTED = "rejected", "Rejected"
    
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='video_calls'
    )
    caller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='initiated_calls'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_calls'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INITIATED
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Call: {self.caller.username} -> {self.receiver.username} ({self.status})"

class CallSession(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='call_session'
    )
    channel_name = models.CharField(max_length=200)
    agora_token = models.TextField()
    doctor_joined = models.BooleanField(default=False)
    patient_joined = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Session: {self.appointment.call_token} - {self.channel_name}"
