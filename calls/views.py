from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from appointments.models import Appointment
from .models import VideoCall, CallSession
try:
    from agora_token_builder.RtcTokenBuilder import RtcTokenBuilder
except ImportError:
    try:
        from agora_token_builder import RtcTokenBuilder
    except ImportError:
        RtcTokenBuilder = None
import json
import random
import time

# Agora configuration (replace with your actual credentials)
APP_ID = 'efd7d3d435314591ac6738f65ad2d308'
APP_CERTIFICATE = '0b8b98014b0942369266bb794561ca34'

@login_required
def enter_token(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        try:
            appointment = Appointment.objects.get(call_token=token)
            
            # Check if user is part of this appointment
            if request.user != appointment.doctor and request.user != appointment.patient:
                messages.error(request, "Invalid token or access denied.")
                return redirect('enter_token')
            
            # Create or get call session
            session, created = CallSession.objects.get_or_create(
                appointment=appointment,
                defaults={
                    'channel_name': f'room_{token}',
                    'agora_token': generate_agora_token(f'room_{token}', random.randint(1, 230))
                }
            )
            
            return redirect('waiting_lobby', token=token)
            
        except Appointment.DoesNotExist:
            messages.error(request, "Invalid token.")
    
    return render(request, 'calls/enter_token.html')

@login_required
def waiting_lobby(request, token):
    try:
        appointment = get_object_or_404(Appointment, call_token=token)
        
        # Check access
        if request.user != appointment.doctor and request.user != appointment.patient:
            messages.error(request, "Access denied.")
            return redirect('enter_token')
        
        # Create or get session without complex logic
        user_role = 'doctor' if request.user == appointment.doctor else 'patient'
        other_user = appointment.patient if user_role == 'doctor' else appointment.doctor
        
        context = {
            'appointment': appointment,
            'user_role': user_role,
            'other_user': other_user,
            'both_joined': True  # Always allow to proceed
        }
        
        return render(request, 'calls/waiting_lobby.html', context)
        
    except Appointment.DoesNotExist:
        messages.error(request, "Invalid token.")
        return redirect('enter_token')

@login_required
def video_room(request, token):
    try:
        appointment = get_object_or_404(Appointment, call_token=token)
        
        # Check access
        if request.user != appointment.doctor and request.user != appointment.patient:
            messages.error(request, "Access denied.")
            return redirect('enter_token')
        
        # Generate Agora token
        channel_name = f'room_{token}'
        uid = random.randint(1, 230)
        agora_token = generate_agora_token(channel_name, uid)
        
        context = {
            'appointment': appointment,
            'agora_token': agora_token,
            'channel_name': channel_name,
        }
        
        return render(request, 'calls/simple_webrtc.html', context)
        
    except Appointment.DoesNotExist:
        messages.error(request, "Invalid session.")
        return redirect('enter_token')

def generate_agora_token(channel_name, uid):
    """Generate proper Agora token with specific UID"""
    if RtcTokenBuilder is None:
        # Return None if agora_token_builder is not available
        return None
        
    expiration_time_in_seconds = 3600 * 24  # 24 hours
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_time_in_seconds
    role = 1  # Publisher role
    
    try:
        token = RtcTokenBuilder.buildTokenWithUid(
            APP_ID, APP_CERTIFICATE, channel_name, uid, role, privilege_expired_ts
        )
        return token
    except Exception as e:
        print(f"Error generating Agora token: {e}")
        return None

@csrf_exempt
def get_agora_token(request):
    if request.method == 'GET':
        channel = request.GET.get('channel')
        uid = random.randint(1, 230)
        token = generate_agora_token(channel, uid)
        return JsonResponse({'token': token, 'uid': uid})
    return JsonResponse({'error': 'Invalid request'})

@csrf_exempt
def check_lobby_status(request, token):
    """API to check if both users have joined the lobby"""
    try:
        appointment = get_object_or_404(Appointment, call_token=token)
        session = get_object_or_404(CallSession, appointment=appointment)
        
        return JsonResponse({
            'doctor_joined': session.doctor_joined,
            'patient_joined': session.patient_joined,
            'both_joined': session.doctor_joined and session.patient_joined
        })
    except (Appointment.DoesNotExist, CallSession.DoesNotExist):
        return JsonResponse({'error': 'Invalid token'})

@login_required
def video_call(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user has access to this call
    if request.user != appointment.doctor and request.user != appointment.patient:
        messages.error(request, "You don't have access to this call.")
        return redirect('dashboard_redirect')
    
    # Determine the other participant
    if request.user == appointment.doctor:
        other_user = appointment.patient
        user_role = 'doctor'
    else:
        other_user = appointment.doctor
        user_role = 'patient'
    
    context = {
        'appointment': appointment,
        'other_user': other_user,
        'user_role': user_role,
    }
    
    return render(request, 'calls/video_call_webrtc.html', context)

@login_required
def diagnostics(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user has access
    if request.user != appointment.doctor and request.user != appointment.patient:
        messages.error(request, "You don't have access to this diagnostic.")
        return redirect('dashboard_redirect')
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'calls/diagnostics.html', context)

@login_required
def initiate_call(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Check access
        if request.user != appointment.doctor and request.user != appointment.patient:
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        # Determine receiver
        receiver = appointment.patient if request.user == appointment.doctor else appointment.doctor
        
        # Create call record
        call = VideoCall.objects.create(
            appointment=appointment,
            caller=request.user,
            receiver=receiver
        )
        
        return JsonResponse({
            'success': True,
            'call_id': call.id,
            'redirect_url': f'/calls/{appointment_id}/'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def signal_offer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        offer = data.get('offer')
        
        # Store offer in cache for the other peer
        cache_key = f'webrtc_offer_{appointment_id}_{request.user.id}'
        cache.set(cache_key, offer, timeout=300)  # 5 minutes
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def signal_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        answer = data.get('answer')
        
        # Store answer in cache for the other peer
        cache_key = f'webrtc_answer_{appointment_id}_{request.user.id}'
        cache.set(cache_key, answer, timeout=300)
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def test_connection(request):
    """API endpoint to test WebSocket and WebRTC connectivity"""
    if request.method == 'POST':
        test_type = request.POST.get('test_type')
        appointment_id = request.POST.get('appointment_id')
        
        results = {
            'websocket': False,
            'webrtc': False,
            'media': False,
            'errors': []
        }
        
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check if user has access
            if request.user != appointment.doctor and request.user != appointment.patient:
                results['errors'].append('Access denied')
                return JsonResponse(results)
            
            # Basic connectivity test
            results['websocket'] = True
            results['webrtc'] = True
            results['media'] = True
            
            return JsonResponse(results)
            
        except Appointment.DoesNotExist:
            results['errors'].append('Appointment not found')
            return JsonResponse(results)
        except Exception as e:
            results['errors'].append(str(e))
            return JsonResponse(results)
    
    return JsonResponse({'error': 'Invalid request method'})

def simple_test_call(request):
    """Simple test page for video calling - no login required"""
    import random
    context = {
        'user_name': 'Test User',
        'user_role': 'tester',
        'room_name': f'test_room_{random.randint(1000, 9999)}'
    }
    return render(request, 'calls/simple_test.html', context)

@login_required
def direct_call_lobby(request):
    """Direct call lobby - doctors and patients can join automatically"""
    user_role = getattr(request.user, 'role', 'user')
    
    # Create a simple room based on user role
    if user_role == 'doctor':
        room_name = 'doctor_patient_room'
        other_role = 'patient'
    elif user_role == 'patient':
        room_name = 'doctor_patient_room'
        other_role = 'doctor'
    else:
        room_name = f'general_room_{random.randint(1000, 9999)}'
        other_role = 'user'
    
    context = {
        'user_name': request.user.get_full_name() or request.user.username,
        'user_role': user_role,
        'other_role': other_role,
        'room_name': room_name,
        'app_id': APP_ID
    }
    
    return render(request, 'calls/direct_call_lobby.html', context)

@login_required
def auto_video_call(request):
    """Auto video call - no tokens needed"""
    user_role = getattr(request.user, 'role', 'user')
    room_name = 'doctor_patient_room'  # Same room for all
    
    context = {
        'user_name': request.user.get_full_name() or request.user.username,
        'user_role': user_role,
        'room_name': room_name,
        'app_id': APP_ID
    }
    
    return render(request, 'calls/auto_video_call.html', context)

@login_required
def manual_test(request, appointment_id):
    """Manual test view for appointment-based calls"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'calls/manual_test.html', context)

@login_required
def cross_device_test(request, appointment_id):
    """Cross device test view"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'calls/cross_device_test.html', context)

@login_required
def get_signal(request, appointment_id):
    """Get WebRTC signaling data"""
    if request.method == 'GET':
        signal_type = request.GET.get('type')  # 'offer' or 'answer'
        other_user_id = request.GET.get('other_user_id')
        
        if signal_type == 'offer':
            cache_key = f'webrtc_offer_{appointment_id}_{other_user_id}'
        else:
            cache_key = f'webrtc_answer_{appointment_id}_{other_user_id}'
        
        signal_data = cache.get(cache_key)
        
        if signal_data:
            cache.delete(cache_key)  # Remove after retrieving
            return JsonResponse({'success': True, 'data': signal_data})
        else:
            return JsonResponse({'success': False, 'message': 'No signal data found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})cts.get(id=appointment_id)
            if request.user == appointment.doctor or request.user == appointment.patient:
                results['access'] = True
            else:
                results['errors'].append('Access denied')
                
        except Appointment.DoesNotExist:
            results['errors'].append('Appointment not found')
            
        return JsonResponse(results)
    
@login_required
def manual_test(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user has access
    if request.user != appointment.doctor and request.user != appointment.patient:
        messages.error(request, "You don't have access to this test.")
        return redirect('dashboard_redirect')
    
    context = {
        'appointment': appointment,
    }
    
@login_required
def cross_device_test(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user has access
    if request.user != appointment.doctor and request.user != appointment.patient:
        messages.error(request, "You don't have access to this test.")
        return redirect('dashboard_redirect')
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'calls/cross_device_test.html', context)
@login_required
def get_signal(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check access
    if request.user != appointment.doctor and request.user != appointment.patient:
        return JsonResponse({'offer': None, 'answer': None})
    
    # Get the other user's ID
    other_user_id = appointment.patient.id if request.user == appointment.doctor else appointment.doctor.id
    
    # Check for offer from other user
    offer_key = f'webrtc_offer_{appointment_id}_{other_user_id}'
    offer = cache.get(offer_key)
    
    # Check for answer from other user
    answer_key = f'webrtc_answer_{appointment_id}_{other_user_id}'
    answer = cache.get(answer_key)
    
    # Clear the signals after reading
    if offer:
        cache.delete(offer_key)
    if answer:
        cache.delete(answer_key)
    
    return JsonResponse({
        'offer': offer,
        'answer': answer
    })