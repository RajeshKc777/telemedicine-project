from django import forms
from django.core.exceptions import ValidationError
from .models import Appointment
from users.models import User
from doctors.models import Availability
from datetime import datetime, time

class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(role='doctor'),
        empty_label="Select Doctor",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(role='patient'),
        empty_label="Select Patient",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'date', 'time', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Optional notes...'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter doctors and patients based on user's role and hospital
        if self.user:
            if self.user.role == 'admin':
                # Admin can create appointments for their hospital patients with any doctor
                self.fields['doctor'].queryset = User.objects.filter(role='doctor')
                self.fields['patient'].queryset = User.objects.filter(
                    role='patient',
                    hospital=self.user.hospital
                )
            elif self.user.role == 'superadmin':
                # Superadmin can create appointments for any patient with any doctor
                pass  # Keep full querysets

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        patient = cleaned_data.get('patient')
        date = cleaned_data.get('date')
        appointment_time = cleaned_data.get('time')

        if doctor and patient and date and appointment_time:
            # Check if doctor is available on this day/time
            day_of_week = date.weekday()  # 0=Monday, 6=Sunday

            # Get doctor's availability for this day
            availabilities = Availability.objects.filter(
                doctor=doctor,
                day_of_week=day_of_week,
                is_available=True
            )

            time_available = False
            for availability in availabilities:
                if availability.start_time <= appointment_time <= availability.end_time:
                    time_available = True
                    break

            if not time_available:
                raise ValidationError("Doctor is not available at this time.")

            # Check for conflicting appointments
            conflicting_appointment = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time=appointment_time,
                status__in=['scheduled', 'completed']
            ).exclude(pk=self.instance.pk if self.instance else None)

            if conflicting_appointment.exists():
                raise ValidationError("Doctor already has an appointment at this time.")

            # Ensure patient doesn't have conflicting appointment
            patient_conflict = Appointment.objects.filter(
                patient=patient,
                date=date,
                time=appointment_time,
                status__in=['scheduled', 'completed']
            ).exclude(pk=self.instance.pk if self.instance else None)

            if patient_conflict.exists():
                raise ValidationError("Patient already has an appointment at this time.")

        return cleaned_data