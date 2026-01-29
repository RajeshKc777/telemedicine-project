from django.db import models
from django.conf import settings

class PatientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'patient'},
        related_name='patient_profile'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    address = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
