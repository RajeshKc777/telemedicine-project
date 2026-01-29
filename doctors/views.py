from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from appointments.models import Appointment
from users.models import User
from hospitals.models import Hospital

@login_required
def manage_availability(request):
    """Simple availability management for doctors"""
    if request.user.role != 'doctor':
        return redirect('dashboard_redirect')
    
    return render(request, 'doctors/manage_availability.html')

@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Only doctors can reschedule their appointments
    if request.user.role != 'doctor' or appointment.doctor != request.user:
        messages.error(request, "You can only reschedule your own appointments.")
        return redirect('dashboard_redirect')
    
    if request.method == 'POST':
        new_date = request.POST.get('date')
        new_time = request.POST.get('time')
        
        # Store original time if not already stored
        if not appointment.original_date:
            appointment.original_date = appointment.date
            appointment.original_time = appointment.time
        
        # Update appointment
        appointment.date = new_date
        appointment.time = new_time
        appointment.modified_by_doctor = True
        appointment.status = 'rescheduled'
        appointment.save()
        
        messages.success(request, 'Appointment rescheduled successfully!')
        return redirect('dashboard_redirect')
    
    return render(request, 'doctors/reschedule_appointment.html', {
        'appointment': appointment
    })

@login_required
def hospital_doctors(request):
    """View for admins to see doctors from other hospitals"""
    if request.user.role not in ['admin', 'superadmin']:
        return redirect('dashboard_redirect')
    
    selected_hospital_id = request.GET.get('hospital')
    hospitals = Hospital.objects.all()
    doctors = []
    
    if selected_hospital_id:
        selected_hospital = get_object_or_404(Hospital, id=selected_hospital_id)
        doctors = User.objects.filter(role='doctor', hospital=selected_hospital)
    
    return render(request, 'users/hospital_doctors.html', {
        'hospitals': hospitals,
        'doctors': doctors,
        'selected_hospital_id': int(selected_hospital_id) if selected_hospital_id else None
    })