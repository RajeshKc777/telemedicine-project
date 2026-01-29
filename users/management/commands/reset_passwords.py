from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Reset passwords for existing users'

    def handle(self, *args, **options):
        # Define password mapping based on roles
        password_map = {
            'superadmin': 'super123',
            'admin': 'admin123', 
            'doctor': 'doctor123',
            'patient': 'patient123'
        }
        
        users = User.objects.all()
        
        self.stdout.write('\n=== CURRENT USERS WITH RESET PASSWORDS ===')
        
        for user in users:
            password = password_map.get(user.role, 'default123')
            user.set_password(password)
            user.save()
            
            self.stdout.write(f'ID: {user.id} | Username: {user.username} | Role: {user.role} | Password: {password}')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully reset passwords for {users.count()} users!'))