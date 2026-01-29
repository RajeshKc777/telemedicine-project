from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import PermissionDenied
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "hospital", "is_staff")
    list_filter = ("role", "hospital", "is_staff", "is_superuser", "is_active")

    fieldsets = UserAdmin.fieldsets + (
        ("Medical Info", {"fields": ("role", "hospital")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Medical Info", {"fields": ("role", "hospital")}),
    )

    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)

    def get_queryset(self, request):
        """Filter queryset based on user permissions"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'admin':
            # Hospital admins can only see users from their hospital
            return qs.filter(hospital=request.user.hospital)
        return qs.none()

    def has_add_permission(self, request):
        """Allow superadmins and hospital admins (with hospitals) to add users"""
        if request.user.is_superuser:
            return True
        elif request.user.role == 'admin' and request.user.hospital:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        """Allow superadmins and hospital admins to change users"""
        if request.user.is_superuser:
            return True
        elif request.user.role == 'admin':
            if obj is None:
                return True
            # Can only change users from their hospital
            return obj.hospital == request.user.hospital
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow superadmins and hospital admins to delete users"""
        if request.user.is_superuser:
            return True
        elif request.user.role == 'admin':
            if obj is None:
                return True
            # Can only delete users from their hospital
            return obj.hospital == request.user.hospital
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limit hospital choices for hospital admins"""
        if db_field.name == "hospital" and not request.user.is_superuser:
            if request.user.role == 'admin' and request.user.hospital:
                # Hospital admins can only assign users to their hospital
                kwargs["queryset"] = db_field.related_model.objects.filter(id=request.user.hospital.id)
            else:
                kwargs["queryset"] = db_field.related_model.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_module_permission(self, request):
        """Allow superadmins and hospital admins to access the admin module"""
        if request.user.is_superuser:
            return True
        elif request.user.role == 'admin' and request.user.hospital:
            return True
        return False

    def save_model(self, request, obj, form, change):
        """Ensure hospital admins can only create users for their hospital"""
        if not request.user.is_superuser and request.user.role == 'admin':
            # Force hospital assignment to admin's hospital
            obj.hospital = request.user.hospital
        super().save_model(request, obj, form, change)
