from django.db import models
from django.conf import settings

class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'doctor'},
        related_name='doctor_profile'
    )
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    biography = models.TextField(blank=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"

class Availability(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'doctor'},
        related_name='availabilities'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ['doctor', 'day_of_week', 'start_time', 'end_time']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.doctor.get_full_name() or self.doctor.username} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
