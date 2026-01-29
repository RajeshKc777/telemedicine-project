from django.db import migrations
from django.contrib.auth import get_user_model

def create_superadmin(apps, schema_editor):
    User = get_user_model()
    if not User.objects.filter(email='admin@admin.com').exists():
        User.objects.create_superuser(
            email='admin@admin.com',
            password='admin123',
            first_name='Super',
            last_name='Admin'
        )

def reverse_superadmin(apps, schema_editor):
    User = get_user_model()
    User.objects.filter(email='admin@admin.com').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_auto_20260127_1959'),
    ]

    operations = [
        migrations.RunPython(create_superadmin, reverse_superadmin),
    ]