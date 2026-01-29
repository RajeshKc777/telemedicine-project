from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from appointments.models import Appointment
from .models import ChatRoom, Message

@login_required
def chat_room(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user has access to this chat
    if request.user != appointment.doctor and request.user != appointment.patient:
        messages.error(request, "You don't have access to this chat.")
        return redirect('dashboard_redirect')
    
    # Get or create chat room
    chat_room, created = ChatRoom.objects.get_or_create(appointment=appointment)
    
    # Get existing messages
    messages_list = Message.objects.filter(chat_room=chat_room).order_by('timestamp')
    last_message_id = messages_list.last().id if messages_list.exists() else 0
    
    # Determine the other participant
    if request.user == appointment.doctor:
        other_user = appointment.patient
        user_role = 'doctor'
    else:
        other_user = appointment.doctor
        user_role = 'patient'
    
    context = {
        'appointment': appointment,
        'chat_room': chat_room,
        'messages': messages_list,
        'other_user': other_user,
        'user_role': user_role,
        'last_message_id': last_message_id,
    }
    
    return render(request, 'chat/chat_room_ajax.html', context)

@login_required
def start_chat(request, doctor_id, patient_id):
    """Start chat between doctor and patient based on their appointment"""
    try:
        # Find appointment between doctor and patient
        appointment = Appointment.objects.filter(
            doctor_id=doctor_id,
            patient_id=patient_id,
            status__in=['scheduled', 'rescheduled']
        ).first()
        
        if not appointment:
            messages.error(request, "No active appointment found between doctor and patient.")
            return redirect('dashboard_redirect')
        
        # Check if user has access
        if request.user.id not in [doctor_id, patient_id]:
            messages.error(request, "You don't have access to this chat.")
            return redirect('dashboard_redirect')
        
        return redirect('chat_room', appointment_id=appointment.id)
        
    except Exception as e:
        messages.error(request, "Error starting chat.")
        return redirect('dashboard_redirect')

@login_required
def chat_list(request):
    """Show available chat partners for doctors and patients"""
    if request.user.role == 'doctor':
        # Get patients from scheduled appointments
        appointments = Appointment.objects.filter(
            doctor=request.user, 
            status__in=['scheduled', 'rescheduled']
        ).select_related('patient')
        chat_partners = [{'user': appt.patient, 'appointment': appt} for appt in appointments]
        title = "Chat with Patients"
        
    elif request.user.role == 'patient':
        # Get doctors from scheduled appointments
        appointments = Appointment.objects.filter(
            patient=request.user, 
            status__in=['scheduled', 'rescheduled']
        ).select_related('doctor')
        chat_partners = [{'user': appt.doctor, 'appointment': appt} for appt in appointments]
        title = "Chat with Doctors"
        
    else:
        messages.error(request, "Chat is only available for doctors and patients.")
        return redirect('dashboard_redirect')
    
    return render(request, 'chat/chat_list.html', {
        'chat_partners': chat_partners,
        'title': title
    })

@login_required
def send_message_ajax(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        message_content = data.get('message')
        
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            if request.user != appointment.doctor and request.user != appointment.patient:
                return JsonResponse({'success': False, 'error': 'Access denied'})
            
            chat_room, created = ChatRoom.objects.get_or_create(appointment=appointment)
            message = Message.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=message_content
            )
            
            return JsonResponse({'success': True, 'message_id': message.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def get_messages_ajax(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        if request.user != appointment.doctor and request.user != appointment.patient:
            return JsonResponse({'messages': []})
        
        chat_room, created = ChatRoom.objects.get_or_create(appointment=appointment)
        last_id = int(request.GET.get('last_id', 0))
        
        messages = Message.objects.filter(
            chat_room=chat_room,
            id__gt=last_id
        ).order_by('timestamp')
        
        messages_data = [{
            'id': msg.id,
            'content': msg.content,
            'sender_id': msg.sender.id,
            'time': msg.timestamp.strftime('%H:%M')
        } for msg in messages]
        
        return JsonResponse({'messages': messages_data})
    except Exception as e:
        return JsonResponse({'messages': []})
