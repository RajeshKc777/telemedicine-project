from django.db import migrations
from django.contrib.auth import get_user_model
from hospitals.models import Hospital

def create_test_users(apps, schema_editor):
    User = get_user_model()
    
    # Create hospital first
    hospital, created = Hospital.objects.get_or_create(
        name="Test Hospital",
        defaults={
            'address': "123 Test Street",
            'phone_number': "555-0123",
            'contact_email': "test@hospital.com"
        }
    )
    
    # Create doctor
    if not User.objects.filter(email='doctor@test.com').exists():
        User.objects.create_user(
            username='doctor',
            email='doctor@test.com',
            password='doctor123',
            first_name='Dr. John',
            last_name='Smith',
            role='doctor',
            hospital=hospital
        )
    
    # Create patient
    if not User.objects.filter(email='patient@test.com').exists():
        User.objects.create_user(
            username='patient',
            email='patient@test.com',
            password='patient123',
            first_name='Jane',
            last_name='Doe',
            role='patient',
            hospital=hospital
        )

def reverse_test_users(apps, schema_editor):
    User = get_user_model()
    User.objects.filter(email__in=['doctor@test.com', 'patient@test.com']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_create_superadmin'),
    ]

    operations = [
        migrations.RunPython(create_test_users, reverse_test_users),
    ]