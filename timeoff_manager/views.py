from django.shortcuts import render, redirect
from django.contrib import messages
from .models import EmployeeProfile, TimeOffRequest
from .services import HCMService
from datetime import datetime, timedelta

def dashboard(request):
    # Fetching the first employee for this demonstration
    employee = EmployeeProfile.objects.first()
    
    if request.method == "POST":
        start_str = request.POST.get('start_date')
        end_str = request.POST.get('end_date')
        attachment = request.FILES.get('attachment') # Get the uploaded file
        
        # Convert strings to date objects
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        
        # --- LOGIC: Calculate Business Days (Skip Sat/Sun) ---
        days_count = 0
        current_day = start_date
        while current_day <= end_date:
            if current_day.weekday() < 5:  # 0-4 are Monday to Friday
                days_count += 1
            current_day += timedelta(days=1)
        
        if days_count == 0:
            messages.error(request, "Selected range contains no business days.")
            return redirect('dashboard')

        # Create the local request record (Pending)
        leave_req = TimeOffRequest.objects.create(
            employee=employee,
            start_date=start_date,
            end_date=end_date,
            days_requested=days_count,
            attachment=attachment,
            status='PENDING'
        )
        
        # Trigger the "Stripe-style" Handshake
        success, message = HCMService.process_leave_request(leave_req.id)
        
        if success:
            messages.success(request, f"Leave Approved for {days_count} business days! {message}")
        else:
            messages.error(request, f"Leave Denied: {message}")
            
        return redirect('dashboard')

    requests = TimeOffRequest.objects.filter(employee=employee).order_by('-created_at')
    return render(request, 'dashboard.html', {
        'employee': employee,
        'requests': requests
    })