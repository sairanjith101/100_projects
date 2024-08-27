from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import LoginForm
from .models import Employee, Department, Attendance
from django.db.models import Q
from django.db import models



# Create your views here.

def home(request):
    return render(request, 'main/index.html')

@login_required
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
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})

@login_required
def profile_info(request):
    try:
        # Get the employee profile associated with the logged-in user
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        # Handle the case where the employee profile does not exist
        employee = None
    return render(request, 'main/profile.html', {'employee':employee})

@login_required
def employees_page(request):
    # Get search criteria from the query parameters
    id_query = request.GET.get('id', '')
    name_query = request.GET.get('name', '')
    email_query = request.GET.get('email', '')
    phone_query = request.GET.get('phone', '')
    position_query = request.GET.get('position', '')

    # Initialize employees variable
    employees = None
    
    # If there is any search criteria, filter the employees
    if id_query or name_query or email_query or phone_query or position_query:
        employees = Employee.objects.all()
        
        if id_query:
            employees = employees.filter(employee_id__icontains=id_query)
        if name_query:
            employees = employees.filter(
                Q(first_name__icontains=name_query) |
                Q(last_name__icontains=name_query)
            )
        if email_query:
            employees = employees.filter(email__icontains=email_query)
        if phone_query:
            employees = employees.filter(phone_number__icontains=phone_query)
        if position_query:
            employees = employees.filter(position__icontains=position_query)

    return render(request, 'main/employees.html', {'employees': employees})


@login_required
def help_page(request):
    return render(request, 'main/help.html')

@login_required
def leave_apply_page(request):
    return render(request, 'main/leave.html')

@login_required
@user_passes_test(lambda user: is_manager(user) or is_team_leader(user))
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

def is_manager(user):
    return user.groups.filter(name='Manager').exists()

def is_team_leader(user):
    return user.groups.filter(name='Team Leader').exists()