from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm
from .models import Employee, Department, Attendance
from django.contrib.auth.decorators import user_passes_test


# Create your views here.

def home(request):
    return render(request, 'main/index.html')

def dashboard(request):
    return render(request, 'main/dashboard.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'main/register.html', {'form': form})

@login_required
def profile_info(request):
    return render(request, 'main/profile.html')

@login_required
def employees_page(request):
    employees = Employee.objects.all()
    return render(request, 'main/employees.html', {'employees': employees})

@login_required
def help_page(request):
    return render(request, 'main/help.html')

@login_required
def leave_apply_page(request):
    return render(request, 'main/leave.html')

@login_required
def head_officers_page(request):
    return render(request, 'main/head_officers.html')

@login_required
def attendance_page(request):
    attendance_records = Attendance.objects.all()
    return render(request, 'main/attendance.html', {'attendance_records': attendance_records})

def logout_view(request):
    logout(request)
    return redirect('login')

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_view(request):
    return render(request, 'main/admin_view.html')
