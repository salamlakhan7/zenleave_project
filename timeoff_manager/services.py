import requests
from decimal import Decimal  # Add this import
from django.db import transaction
from .models import TimeOffRequest, EmployeeProfile

class HCMService:
    @staticmethod
    def get_realtime_hcm_balance(employee_id, location_id):
        # Wrap the mock return in Decimal()
        return Decimal('15.0') 

    @staticmethod
    @transaction.atomic
    def process_leave_request(request_id):
        leave_req = TimeOffRequest.objects.select_for_update().get(id=request_id)
        employee = leave_req.employee

        hcm_balance = HCMService.get_realtime_hcm_balance(employee.employee_id, employee.location_id)
        
        # Ensure comparison is Decimal vs Decimal
        if employee.leave_balance != hcm_balance:
            employee.leave_balance = hcm_balance
            employee.save()

        # Convert days_requested to Decimal just in case
        days_to_deduct = Decimal(str(leave_req.days_requested))

        if hcm_balance < days_to_deduct:
            leave_req.status = 'REJECTED'
            leave_req.save()
            return False, "Insufficient Balance"

        # Approval Handshake logic
        leave_req.status = 'APPROVED'
        leave_req.hcm_reference_id = "HCM-REF-SUCCESS"
        
        # Now this math will work because both are Decimals
        employee.leave_balance -= days_to_deduct
        employee.save()
        leave_req.save()
        
        return True, "Sync Successful"