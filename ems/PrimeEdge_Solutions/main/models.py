from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Employee(models.Model):
    first_name = models.CharField(max_length=50, null=False, blank=False, default='FirstName')
    last_name = models.CharField(max_length=50, null=False, blank=False, default='LastName')
    email = models.EmailField(unique=True, default='default@example.com')
    phone_number = models.CharField(max_length=15, null=False, blank=False)
    position = models.CharField(max_length=100, null=False, blank=False, default='Unknown Position')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    date_of_birth = models.DateField(default=date.today)
    date_of_joining = models.DateField(default=date.today)
    address = models.CharField(max_length=255, default='Unknown Address')
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, default='00000')
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('On Leave', 'On Leave'), ('Inactive', 'Inactive')], default='Active')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['last_name', 'first_name']

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10)
