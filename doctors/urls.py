from django.urls import path
from . import views

urlpatterns = [
    path('manage-availability/', views.manage_availability, name='manage_availability'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
]