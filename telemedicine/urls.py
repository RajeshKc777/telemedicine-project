"""
URL configuration for telemedicine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users.views import dashboard_redirect
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),

    # Explicit auth endpoints
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Role-based redirect at root
    path('', dashboard_redirect, name='dashboard_redirect'),

    # Keep including app urls if needed
    path('', include('users.urls')),
    path('appointments/', include('appointments.urls')),
    path('doctors/', include('doctors.urls')),
    path('chat/', include('chat.urls')),
    path('calls/', include('calls.urls')),
    path('hospitals/', include('hospitals.urls')),
]
