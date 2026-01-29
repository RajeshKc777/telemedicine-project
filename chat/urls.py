from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:appointment_id>/', views.chat_room, name='chat_room'),
    path('start/<int:doctor_id>/<int:patient_id>/', views.start_chat, name='start_chat'),
    path('send-message/', views.send_message_ajax, name='send_message_ajax'),
    path('get-messages/<int:appointment_id>/', views.get_messages_ajax, name='get_messages_ajax'),
]