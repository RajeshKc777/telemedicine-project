from django.urls import path
from . import views

urlpatterns = [
    # Token-based video calling
    path('enter-token/', views.enter_token, name='enter_token'),
    path('lobby/<str:token>/', views.waiting_lobby, name='waiting_lobby'),
    path('room/<str:token>/', views.video_room, name='video_room'),
    path('api/lobby-status/<str:token>/', views.check_lobby_status, name='check_lobby_status'),
    path('api/agora-token/', views.get_agora_token, name='get_agora_token'),
    
    # Legacy video call routes
    path('<int:appointment_id>/', views.video_call, name='video_call'),
    path('<int:appointment_id>/diagnostics/', views.diagnostics, name='call_diagnostics'),
    path('<int:appointment_id>/test/', views.manual_test, name='manual_test'),
    path('<int:appointment_id>/cross-device/', views.cross_device_test, name='cross_device_test'),
    path('initiate/', views.initiate_call, name='initiate_call'),
    path('signal/offer/', views.signal_offer, name='signal_offer'),
    path('signal/answer/', views.signal_answer, name='signal_answer'),
    path('signal/<int:appointment_id>/', views.get_signal, name='get_signal'),
    path('test/', views.test_connection, name='test_connection'),
]