from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_appointment, name='create_appointment'),
    path('<int:appointment_id>/edit/', views.edit_appointment, name='edit_appointment'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('<int:appointment_id>/mark-done/', views.mark_as_done, name='mark_as_done'),
    path('send-request/', views.send_appointment_request, name='send_appointment_request'),
    path('doctor-requests/', views.doctor_requests, name='doctor_requests'),
    path('handle-request/<int:request_id>/', views.handle_request, name='handle_request'),
]