from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Appointment, AppointmentRequest
from .forms import AppointmentForm
from users.models import User

@login_required
def create_appointment(request):
    # Only admins and superadmins can create appointments
    if request.user.role not in ['admin', 'superadmin']:
        messages.error(request, "You don't have permission to create appointments.")
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            # Set hospital based on doctor
            appointment.hospital = appointment.doctor.hospital
            appointment.created_by = request.user
            appointment.save()
            messages.success(request, f"Appointment created successfully for {appointment.patient.get_full_name() or appointment.patient.username} with Dr. {appointment.doctor.get_full_name() or appointment.doctor.username}.")
            return redirect('appointment_list')
    else:
        form = AppointmentForm(user=request.user)

    return render(request, 'appointments/create_appointment.html', {
        'form': form,
        'title': 'Create New Appointment'
    })

@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Permission checks
    if request.user.role == 'admin':
        if appointment.hospital != request.user.hospital:
            messages.error(request, "You can only edit appointments for your hospital.")
            return redirect('appointment_list')
    elif request.user.role not in ['admin', 'superadmin']:
        messages.error(request, "You don't have permission to edit appointments.")
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.hospital = appointment.doctor.hospital
            appointment.save()
            messages.success(request, "Appointment updated successfully.")
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment, user=request.user)

    return render(request, 'appointments/create_appointment.html', {
        'form': form,
        'title': 'Edit Appointment',
        'appointment': appointment
    })

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Permission checks
    if request.user.role == 'patient' and appointment.patient != request.user:
        messages.error(request, "You can only cancel your own appointments.")
        return redirect('dashboard_redirect')
    elif request.user.role == 'doctor' and appointment.doctor != request.user:
        messages.error(request, "You can only cancel your own appointments.")
        return redirect('dashboard_redirect')
    elif request.user.role == 'admin':
        if appointment.hospital != request.user.hospital:
            messages.error(request, "You can only cancel appointments for your hospital.")
            return redirect('appointment_list')
    elif request.user.role not in ['admin', 'superadmin', 'doctor', 'patient']:
        messages.error(request, "You don't have permission to cancel appointments.")
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, "Appointment cancelled successfully.")
        return redirect('appointment_list')

    return render(request, 'appointments/cancel_appointment.html', {
        'appointment': appointment
    })

@login_required
def send_appointment_request(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        patient_id = request.POST.get('patient_id')
        date = request.POST.get('date')
        time = request.POST.get('time')
        message = request.POST.get('message')
        
        doctor = get_object_or_404(User, id=doctor_id, role='doctor')
        patient = get_object_or_404(User, id=patient_id, role='patient')
        
        AppointmentRequest.objects.create(
            doctor=doctor,
            patient=patient,
            requested_by=request.user,
            requested_date=date,
            requested_time=time,
            message=message
        )
        
        messages.success(request, f'Appointment request sent to Dr. {doctor.get_full_name() or doctor.username}')
        return redirect('hospital_doctors')
    
    return redirect('hospital_doctors')

@login_required
def doctor_requests(request):
    if request.user.role != 'doctor':
        return redirect('dashboard_redirect')
    
    requests = AppointmentRequest.objects.filter(doctor=request.user)
    return render(request, 'appointments/doctor_requests.html', {
        'requests': requests
    })

@login_required
def handle_request(request, request_id):
    if request.user.role != 'doctor':
        return redirect('dashboard_redirect')
    
    appointment_request = get_object_or_404(AppointmentRequest, id=request_id, doctor=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            # Generate 4-digit token
            call_token = str(random.randint(1000, 9999))
            
            # Create actual appointment
            appointment = Appointment.objects.create(
                doctor=appointment_request.doctor,
                patient=appointment_request.patient,
                hospital=appointment_request.doctor.hospital,
                date=appointment_request.requested_date,
                time=appointment_request.requested_time,
                notes=appointment_request.message,
                created_by=appointment_request.requested_by,
                call_token=call_token
            )
            
            appointment_request.status = 'approved'
            appointment_request.approved_date = appointment_request.requested_date
            appointment_request.approved_time = appointment_request.requested_time
            appointment_request.save()
            
            messages.success(request, 'Appointment request approved!')
            
        elif action == 'modify':
            new_date = request.POST.get('new_date')
            new_time = request.POST.get('new_time')
            doctor_response = request.POST.get('doctor_response')
            
            appointment_request.status = 'modified'
            appointment_request.approved_date = new_date
            appointment_request.approved_time = new_time
            appointment_request.doctor_response = doctor_response
            appointment_request.save()
            
            messages.success(request, 'Appointment request modified!')
            
        elif action == 'reject':
            doctor_response = request.POST.get('doctor_response')
            appointment_request.status = 'rejected'
            appointment_request.doctor_response = doctor_response
            appointment_request.save()
            
            messages.success(request, 'Appointment request rejected!')
        
        return redirect('doctor_requests')
    
    return render(request, 'appointments/handle_request.html', {
        'appointment_request': appointment_request
    })

@login_required
def mark_as_done(request, appointment_id):
    if request.user.role != 'doctor':
        return redirect('dashboard_redirect')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    
    if request.method == 'POST':
        consultation_notes = request.POST.get('consultation_notes')
        appointment.consultation_notes = consultation_notes
        appointment.status = 'done'
        appointment.save()
        
        messages.success(request, 'Appointment marked as done!')
        return redirect('dashboard_redirect')
    
    return render(request, 'appointments/mark_as_done.html', {
        'appointment': appointment
    })