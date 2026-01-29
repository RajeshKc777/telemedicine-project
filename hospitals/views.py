from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Hospital

def is_superadmin(user):
    return getattr(user, 'role', None) == 'superadmin'

@login_required
@user_passes_test(is_superadmin)
def create_hospital(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        
        try:
            # Check if hospital with same name exists
            if Hospital.objects.filter(name=name).exists():
                messages.error(request, 'A hospital with this name already exists!')
                return render(request, 'hospitals/create_hospital.html')
            
            # Create hospital
            Hospital.objects.create(
                name=name,
                address=address,
                phone=phone,
                email=email
            )
            
            messages.success(request, 'Hospital created successfully!')
            return redirect('dashboard_redirect')
            
        except Exception as e:
            messages.error(request, f'Error creating hospital: {str(e)}')
            return render(request, 'hospitals/create_hospital.html')
    
    return render(request, 'hospitals/create_hospital.html')

@login_required
@user_passes_test(is_superadmin)
def manage_hospitals(request):
    hospitals = Hospital.objects.all().order_by('name')
    return render(request, 'hospitals/manage_hospitals.html', {'hospitals': hospitals})