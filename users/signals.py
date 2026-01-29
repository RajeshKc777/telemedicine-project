from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from doctors.models import DoctorProfile
from patients.models import PatientProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Roles.DOCTOR:
            DoctorProfile.objects.get_or_create(user=instance)
        elif instance.role == User.Roles.PATIENT:
            PatientProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == User.Roles.DOCTOR:
        if hasattr(instance, 'doctor_profile'):
            instance.doctor_profile.save()
    elif instance.role == User.Roles.PATIENT:
        if hasattr(instance, 'patient_profile'):
            instance.patient_profile.save()
