from django.core.management.base import BaseCommand
from decimal import Decimal
from timeoff_manager.models import EmployeeProfile

class Command(BaseCommand):
    help = 'Processes the massive HCM balance corpus safely'

    def handle(self, *args, **options):
        # Simulated data dump from HCM
        hcm_data_dump = [
            {'emp_id': 'EMP-777', 'loc_id': 'NY-01', 'balance': '25.50'},
            {'emp_id': 'EMP-101', 'loc_id': 'LDN-02', 'balance': '12.00'}, # This one failed before
        ]

        self.stdout.write("--- Starting Defensive Batch Corpus Sync ---")

        for record in hcm_data_dump:
            # Check if this employee already exists in our system
            employee_exists = EmployeeProfile.objects.filter(employee_id=record['emp_id']).exists()

            if employee_exists:
                # If they exist, update their balance to match the "Source of Truth"
                EmployeeProfile.objects.filter(employee_id=record['emp_id']).update(
                    location_id=record['loc_id'],
                    leave_balance=Decimal(record['balance'])
                )
                self.stdout.write(self.style.SUCCESS(f"UPDATED: {record['emp_id']} balance set to {record['balance']}"))
            else:
                # If they don't exist, we skip them to avoid the IntegrityError (No User)
                # In a real system, you might create a 'Pending' account here.
                self.stdout.write(self.style.WARNING(f"SKIPPED: {record['emp_id']} - No matching local user account found."))

        self.stdout.write("--- Sync Completed ---")