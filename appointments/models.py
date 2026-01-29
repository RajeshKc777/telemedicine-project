from django.db import models
from django.conf import settings
from hospitals.models import Hospital

class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        RESCHEDULED = "rescheduled", "Rescheduled"
        DONE = "done", "Done"

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'doctor'},
        related_name='doctor_appointments'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='patient_appointments'
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    notes = models.TextField(blank=True)
    consultation_notes = models.TextField(blank=True, help_text='Doctor findings and outcome')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_appointments',
        help_text='Admin or superadmin who created this appointment'
    )
    is_cross_hospital = models.BooleanField(
        default=False,
        help_text='True if patient and doctor are from different hospitals'
    )
    original_date = models.DateField(null=True, blank=True)
    original_time = models.TimeField(null=True, blank=True)
    modified_by_doctor = models.BooleanField(default=False)
    call_token = models.CharField(max_length=4, blank=True, null=True, help_text='4-digit token for video call')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date}"
    
    def save(self, *args, **kwargs):
        # Check if this is cross-hospital appointment
        if self.patient.hospital != self.doctor.hospital:
            self.is_cross_hospital = True
        super().save(*args, **kwargs)

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