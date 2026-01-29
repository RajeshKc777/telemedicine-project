from django import forms
from .models import Availability

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['day_of_week', 'start_time', 'end_time', 'is_available']
        widgets = {
            'day_of_week': forms.Select(choices=Availability.DAYS_OF_WEEK),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'is_available': forms.CheckboxInput(),
        }