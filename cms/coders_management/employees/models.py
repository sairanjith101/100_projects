from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=10, unique=True)
    extension_number = models.CharField(max_length=5, blank=True)
    tl_name = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True)

    def __str__(self) -> str:
        return f'{self.user.username} - {self.employee_id}'