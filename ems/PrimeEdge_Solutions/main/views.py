from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import LoginForm, AttendanceForm, LeaveApprovalForm, LeaveRequestForm
from .models import Employee, Department, Attendance, LeaveRequest
from django.db.models import Q
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from django.contrib import messages



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
def leave_page(request):
    user = request.user
    employee = get_object_or_404(Employee, user=user)
    
    # Determine the role based on position
    position = employee.position.lower()
    
    if 'manager' in position:
        role = 'Manager'
    elif 'team lead' in position or 'tl' in position:
        role = 'Team Lead'
    else:
        role = 'Employee'
    
    if request.method == 'POST':
        if role == 'Employee' and 'apply_leave' in request.POST:
            form = LeaveRequestForm(request.POST)
            if form.is_valid():
                leave_request = form.save(commit=False)
                leave_request.employee = employee
                leave_request.status = 'Pending'
                leave_request.save()
                messages.success(request, 'Leave request submitted successfully.')
                return redirect('leave_page')
        
        elif role in ['Team Lead', 'Manager'] and 'process_leave' in request.POST:
            leave_request_id = request.POST.get('leave_request_id')
            action = request.POST.get('process_leave')
            leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
            
            if role == 'Manager' and leave_request.status == 'Approved by TL':
                leave_request.status = 'Approved by Manager'
                messages.success(request, 'Leave request approved by Manager.')
            elif role == 'Team Lead':
                if action == 'approve':
                    leave_request.status = 'Approved by TL'
                    messages.success(request, 'Leave request approved by TL.')
                elif action == 'reject':
                    leave_request.status = 'Rejected'
                    messages.success(request, 'Leave request rejected by TL.')
            leave_request.processed_on = timezone.now()
            leave_request.save()
            return redirect('leave_page')

    else:
        form = LeaveRequestForm() if role == 'Employee' else LeaveApprovalForm()

    leave_requests = LeaveRequest.objects.filter(employee=employee) if role == 'Employee' else LeaveRequest.objects.filter(status='Pending')
    approved_requests = LeaveRequest.objects.exclude(status='Pending')

    return render(request, 'main/leave.html', {
        'form': form,
        'leave_requests': leave_requests,
        'approved_requests': approved_requests,
        'is_employee': role == 'Employee',
        'is_team_leader': role == 'Team Lead',
        'is_manager': role == 'Manager',
    })





@login_required
@user_passes_test(lambda user: is_manager(user) or is_team_leader(user))
def head_officers_page(request):
    return render(request, 'main/head_officers.html')

@login_required
def attendance_page(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        employee = None

    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)

    if request.method == 'POST':
        if 'check_in' in request.POST:
            if attendance.check_in_time is None:
                attendance.check_in_time = timezone.now().time()
                attendance.status = 'Present'
                attendance.save()
                employee.status = 'Active'
                employee.save()

        elif 'check_out' in request.POST:
            if attendance.check_in_time is not None and attendance.check_out_time is None:
                attendance.check_out_time = timezone.now().time()
                attendance.status = 'Present' if attendance.check_in_time else 'Absent'
                attendance.save()
                employee.status = 'Inactive'
                employee.save()

        return redirect('attendance')

    # Determine the view type
    view_type = request.GET.get('view', 'table')
    
    # Get all attendance records for the current month
    attendance_records = Attendance.objects.filter(employee=employee, date__month=today.month).order_by('-date')

    return render(request, 'main/attendance.html', {
        'employee': employee,
        'attendance': attendance,
        'attendance_records': attendance_records,
        'view_type': view_type,
    })

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