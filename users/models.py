from django.contrib.auth.models import AbstractUser
from django.db import models
from hospitals.models import Hospital


class User(AbstractUser):
    class Roles(models.TextChoices):
        SUPERADMIN = "superadmin", "Super Admin"
        ADMIN = "admin", "Admin"
        DOCTOR = "doctor", "Doctor"
        PATIENT = "patient", "Patient"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.PATIENT,
        help_text="User role controls dashboard access",
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
        help_text="The hospital this user belongs to (required for Admin, Doctor, Patient)",
    )

    def is_superadmin(self):
        return self.role == self.Roles.SUPERADMIN

    def is_admin(self):
        return self.role == self.Roles.ADMIN

    def is_doctor(self):
        return self.role == self.Roles.DOCTOR

    def is_patient(self):
        return self.role == self.Roles.PATIENT
