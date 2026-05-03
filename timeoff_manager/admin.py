from django.contrib import admin
from timeoff_manager import models
# Register your models here.

admin.site.register(models.EmployeeProfile)
admin.site.register(models.TimeOffRequest)