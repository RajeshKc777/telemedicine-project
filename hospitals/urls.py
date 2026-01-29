from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_hospital, name='create_hospital'),
    path('manage/', views.manage_hospitals, name='manage_hospitals'),
]