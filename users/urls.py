from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('create-admin/', views.create_hospital_admin, name='create_hospital_admin'),
    path('create-doctor/', views.create_doctor, name='create_doctor'),
    path('create-patient/', views.create_patient, name='create_patient'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('patients/', views.patient_list, name='patient_list'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('hospital-doctors/', views.hospital_doctors, name='hospital_doctors'),
    path('', views.dashboard_redirect, name='dashboard_redirect'),
]
