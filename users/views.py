from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from .models import User
from .forms import AdminCreationForm
from hospitals.models import Hospital
from appointments.models import Appointment, AppointmentRequest

def is_superadmin(user):
    return getattr(user, 'role', None) == 'superadmin'

def is_admin_or_superadmin(user):
    return getattr(user, 'role', None) in ['admin', 'superadmin']

@login_required
def dashboard_redirect(request):
    user = request.user
    role = getattr(user, 'role', None)
    today = timezone.now().date()

    if role == 'superadmin':
        return render(request, 'dashboards/superadmin_dashboard.html', {
            'hospitals_count': Hospital.objects.count(),
            'admins_count': User.objects.filter(role='admin').count(),
            'users_count': User.objects.count(),
        })

    if role == 'admin':
        hospital = user.hospital
        if not hospital:
            # If admin has no hospital, assign them to first available hospital
            hospital = Hospital.objects.first()
            if hospital:
                user.hospital = hospital
                user.save()
        
        return render(request, 'dashboards/admin_dashboard.html', {
            'hospital': hospital,
            'doctors_count': User.objects.filter(role='doctor', hospital=hospital).count() if hospital else 0,
            'patients_count': User.objects.filter(role='patient', hospital=hospital).count() if hospital else 0,
            'appointments_count': Appointment.objects.filter(hospital=hospital).count() if hospital else 0,
            'active_today_count': Appointment.objects.filter(hospital=hospital, date=today).count() if hospital else 0,
        })

    if role == 'doctor':
        pending_requests = AppointmentRequest.objects.filter(doctor=user, status='pending')
        # Get patients from scheduled appointments
        scheduled_appointments = Appointment.objects.filter(doctor=user, status__in=['scheduled', 'rescheduled'])
        available_patients = [appt.patient for appt in scheduled_appointments]
        return render(request, 'dashboards/doctor_dashboard.html', {
            'appointments_today': Appointment.objects.filter(doctor=user, date=today, status__in=['scheduled', 'rescheduled']).order_by('time'),
            'total_appointments': Appointment.objects.filter(doctor=user, status='done').count(),
            'pending_requests': pending_requests,
            'pending_requests_count': pending_requests.count(),
            'available_patients': available_patients,
        })

    if role == 'patient':
        # Get doctors from scheduled appointments
        scheduled_appointments = Appointment.objects.filter(patient=user, status__in=['scheduled', 'rescheduled'])
        available_doctors = [appt.doctor for appt in scheduled_appointments]
        return render(request, 'dashboards/patient_dashboard.html', {
            'upcoming_appointments': Appointment.objects.filter(patient=user, date__gte=today).order_by('date', 'time'),
            'available_doctors': available_doctors,
        })

    if getattr(user, 'is_superuser', False):
        return redirect('/admin/')
    
    return redirect('login')

@login_required
def doctor_list(request):
    user = request.user
    if user.role not in ['superadmin', 'admin']:
        return redirect('dashboard_redirect')
    
    if user.role == 'superadmin':
        doctors = User.objects.filter(role='doctor')
    else:
        doctors = User.objects.filter(role='doctor', hospital=user.hospital)
        
    return render(request, 'users/doctor_list.html', {'doctors': doctors})

@login_required
def patient_list(request):
    user = request.user
    if user.role not in ['superadmin', 'admin', 'doctor']:
        return redirect('dashboard_redirect')
        
    if user.role == 'superadmin':
        patients = User.objects.filter(role='patient')
    else:
        patients = User.objects.filter(role='patient', hospital=user.hospital)
        
    return render(request, 'users/patient_list.html', {'patients': patients})

@login_required
def appointment_list(request):
    user = request.user
    today = timezone.now().date()
    
    if user.role == 'superadmin':
        appointments = Appointment.objects.all()
        completed_appointments = None
    elif user.role == 'admin':
        appointments = Appointment.objects.filter(hospital=user.hospital)
        completed_appointments = None
    elif user.role == 'doctor':
        appointments = Appointment.objects.filter(doctor=user)
        completed_appointments = Appointment.objects.filter(doctor=user, status='done').order_by('-date', '-time')
    else: # Patient
        appointments = Appointment.objects.filter(patient=user)
        completed_appointments = None
        
    return render(request, 'users/appointment_list.html', {
        'appointments': appointments.order_by('-date', '-time'),
        'completed_appointments': completed_appointments,
        'today': today
    })

@login_required
@user_passes_test(is_superadmin)
def manage_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users/manage_users.html', {'users': users})

@login_required
@user_passes_test(is_superadmin)
def create_hospital_admin(request):
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hospital admin created successfully!')
            return redirect('manage_users')
    else:
        form = AdminCreationForm()
    return render(request, 'users/create_admin.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_superadmin)
def create_doctor(request):
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        specialization = request.POST.get('specialization')
        license_number = request.POST.get('license_number')
        
        try:
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists!')
                return render(request, 'users/create_doctor.html')
            
            # Check if license number already exists
            from doctors.models import DoctorProfile
            if license_number and DoctorProfile.objects.filter(license_number=license_number).exists():
                messages.error(request, 'A doctor with this license number already exists!')
                return render(request, 'users/create_doctor.html')
            
            # Generate unique username from email
            username = email.split('@')[0]
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=User.Roles.DOCTOR,
                hospital=request.user.hospital
            )
            
            # Create doctor profile
            DoctorProfile.objects.create(
                user=user,
                specialization=specialization,
                license_number=license_number
            )
            
            messages.success(request, 'Doctor created successfully!')
            return redirect('doctor_list')
            
        except Exception as e:
            messages.error(request, f'Error creating doctor: {str(e)}')
            return render(request, 'users/create_doctor.html')
    
    return render(request, 'users/create_doctor.html')

@login_required
@user_passes_test(is_admin_or_superadmin)
def create_patient(request):
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        date_of_birth = request.POST.get('date_of_birth') or None
        blood_group = request.POST.get('blood_group', '')
        
        try:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists!')
                return render(request, 'users/create_patient.html')
            
            # Generate unique username from email
            username = email.split('@')[0]
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=User.Roles.PATIENT,
                hospital=request.user.hospital
            )
            
            # Create patient profile only if user was created successfully
            from patients.models import PatientProfile
            PatientProfile.objects.create(
                user=user,
                date_of_birth=date_of_birth,
                blood_group=blood_group
            )
            
            messages.success(request, 'Patient created successfully!')
            return redirect('patient_list')
            
        except Exception as e:
            messages.error(request, f'Error creating patient: {str(e)}')
            return render(request, 'users/create_patient.html')
    
    return render(request, 'users/create_patient.html')

@login_required
def hospital_doctors(request):
    """View for admins to see doctors from other hospitals"""
    if request.user.role not in ['admin', 'superadmin']:
        return redirect('dashboard_redirect')
    
    selected_hospital_id = request.GET.get('hospital')
    hospitals = Hospital.objects.all()
    doctors = []
    admin_requests = []
    
    if selected_hospital_id:
        selected_hospital = get_object_or_404(Hospital, id=selected_hospital_id)
        doctors = User.objects.filter(role='doctor', hospital=selected_hospital)
    
    # Get admin's sent requests
    admin_requests = AppointmentRequest.objects.filter(requested_by=request.user).order_by('-created_at')
    
    return render(request, 'users/hospital_doctors.html', {
        'hospitals': hospitals,
        'doctors': doctors,
        'admin_requests': admin_requests,
        'selected_hospital_id': int(selected_hospital_id) if selected_hospital_id else None
    })

@login_required
@user_passes_test(is_superadmin)
def manage_hospitals(request):
    return render(request, 'dashboards/superadmin_dashboard.html', {'message': 'Hospital management coming in Step 2'})

@login_required
@user_passes_test(is_superadmin)
def assign_hospital_admins(request):
    return render(request, 'dashboards/superadmin_dashboard.html', {'message': 'Assigning admins to hospitals coming in Step 2'})

@login_required
@user_passes_test(is_superadmin)
def assign_roles(request):
    return render(request, 'dashboards/superadmin_dashboard.html', {'message': 'Role assignment refinement coming in Step 2'})
