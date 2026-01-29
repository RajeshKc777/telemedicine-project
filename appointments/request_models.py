from django.db import models
from django.conf import settings
from hospitals.models import Hospital

class AppointmentRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        MODIFIED = "modified", "Modified"

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'doctor'},
        related_name='appointment_requests'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='patient_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_requests'
    )
    requested_date = models.DateField()
    requested_time = models.TimeField()
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    doctor_response = models.TextField(blank=True)
    approved_date = models.DateField(null=True, blank=True)
    approved_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request: {self.patient} with {self.doctor} on {self.requested_date}"