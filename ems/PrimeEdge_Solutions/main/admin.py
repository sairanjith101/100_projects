from django.contrib import admin
from .models import Employee, Company, Attendance

# Register your models here.

admin.site.register(Employee)
admin.site.register(Company)
admin.site.register(Attendance)