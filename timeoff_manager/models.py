from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class EmployeeProfile(models.Model):
    # Link to Django's built-in User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Required for the HCM sync: Balances are per-employee per-location
    employee_id = models.CharField(max_length=50, unique=True)
    location_id = models.CharField(max_length=50)
    
    # The "Shadow Balance" - local copy of HCM truth
    leave_balance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    last_synced_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

class TimeOffRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SYNC_ERROR', 'Sync Error'), # Defensive state for failed HCM handshake
    ]
    
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='requests')
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.DecimalField(max_digits=4, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # HCM specific tracking
    hcm_reference_id = models.CharField(max_length=100, null=True, blank=True)
    reason = models.TextField(blank=True)
    
    # Media for evidence/documentation as requested
    attachment = models.FileField(upload_to='leave_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.start_date} ({self.status})"