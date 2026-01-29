from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'hospital', 'date', 'time', 'status')
    list_filter = ('status', 'date', 'hospital')
    search_fields = ('patient__username', 'doctor__username', 'hospital__name')
