from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import User

class BaseUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-blue focus:border-transparent',
        'placeholder': 'Enter strong password'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-blue focus:border-transparent',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-blue focus:border-transparent',
                'placeholder': 'Email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-blue focus:border-transparent',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-blue focus:border-transparent',
                'placeholder': 'Last Name'
            }),
        }

class AdminCreationForm(BaseUserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Roles.ADMIN
        user.is_staff = True
        if commit:
            user.save()
            content_type = ContentType.objects.get_for_model(User)
            permissions = Permission.objects.filter(content_type=content_type)
            user.user_permissions.add(*permissions)
        return user

class DoctorCreationForm(BaseUserCreationForm):
    specialization = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-blue focus:border-transparent',
        'placeholder': 'e.g., Cardiology, Pediatrics'
    }))
    license_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-blue focus:border-transparent',
        'placeholder': 'Medical License Number'
    }))
    
    def __init__(self, hospital=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hospital = hospital
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Roles.DOCTOR
        user.hospital = self.hospital
        if commit:
            user.save()
            from doctors.models import DoctorProfile
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                license_number=self.cleaned_data['license_number']
            )
        return user

class PatientCreationForm(BaseUserCreationForm):
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-blue focus:border-transparent',
        'type': 'date'
    }))
    blood_group = forms.CharField(max_length=5, required=False, widget=forms.TextInput(attrs={
        'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-blue focus:border-transparent',
        'placeholder': 'e.g., A+, B-, O+'
    }))
    
    def __init__(self, hospital=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hospital = hospital
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Roles.PATIENT
        user.hospital = self.hospital
        if commit:
            user.save()
            from patients.models import PatientProfile
            PatientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                blood_group=self.cleaned_data.get('blood_group', '')
            )
        return user
