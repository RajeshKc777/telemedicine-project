from django.contrib import admin
from .models import DoctorProfile

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'license_number')
    search_fields = ('user__username', 'specialization', 'license_number')
    list_filter = ('specialization',)
