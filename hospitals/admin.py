from django.contrib import admin
from .models import Hospital

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'phone_number', 'created_at')
    search_fields = ('name', 'contact_email')
