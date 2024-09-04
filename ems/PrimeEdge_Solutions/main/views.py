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
from django.http import JsonResponse



# Create your views here.

def home(request):
    return render(request, 'main/index.html')

def redirect_to_dashboard(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')
    

@login_required
def dashboard(request):
    today = timezone.now().date()
    
    # Total count of employees
    total_employees = Employee.objects.count()
    
    # Employees who have checked in today
    checked_in_employee_ids = Attendance.objects.filter(date=today).values_list('employee_id', flat=True).distinct()
    checked_in_count = Employee.objects.filter(id__in=checked_in_employee_ids).count()
    
    # Employees who have not checked in today
    not_checked_in_count = Employee.objects.exclude(id__in=checked_in_employee_ids).count()
    
    context = {
        'total_employees': total_employees,
        'checked_in_count': checked_in_count,
        'not_checked_in_count': not_checked_in_count,
    }

    return render(request, 'main/dashboard.html', context)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request,"Logged in Successfully")
                return redirect('dashboard')
            else:
                messages.error(request,"Invalid User Name and Password")
                return redirect("login")
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
    department_query = request.GET.get('department', '')

    # Initialize employees variable
    employees = None
    
    # If there is any search criteria, filter the employees
    if id_query or name_query or email_query or phone_query or position_query or department_query:
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
            employees = employees.filter(position__name__icontains=position_query)
        if department_query:
            employees = employees.filter(department__name__icontains=department_query)

        if not employees.exists():
            messages.warning(request, "No employees found with the given search criteria.")

    return render(request, 'main/employees.html', {'employees': employees})


@login_required
def help_page(request):
    return render(request, 'main/help.html')

@login_required
def leave_request(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            
            # Get the employee submitting the request
            employee = Employee.objects.get(user=request.user)

            if LeaveRequest.objects.filter(
                employee=employee, 
                start_date__lte=leave_request.end_date, 
                end_date__gte=leave_request.start_date
            ).exists():
                messages.error(request, 'A leave request for the selected date range already exists.')
                # Don't redirect; simply re-render the form with the error message
                leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-applied_on')
                return render(request, 'main/leave.html', {
                    'form': form,
                    'leave_requests': leave_requests,
                })
            
            # Find the team lead for the employee's department
            team_lead = Employee.objects.filter(position__name='Team Lead', department=employee.department).first()
            
            if team_lead:
                leave_request.employee = employee
                leave_request.tl = team_lead  # Assign the Team Lead to the request
                leave_request.save()
                messages.success(request, 'Leave request submitted successfully. Please wait for approval.')
                return redirect('leave_page')  # Redirect after submission
            else:
                messages.error(request, 'No Team Lead assigned to your department. Please contact HR.')
                return render(request, 'main/leave.html', {
                    'form': form,
                })
    else:
        form = LeaveRequestForm()

    # Fetch the leave requests of the logged-in employee
    employee = Employee.objects.get(user=request.user)
    leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-applied_on')

    return render(request, 'main/leave.html', {
        'form': form,
        'leave_requests': leave_requests,
    })

@login_required
def head_officers(request):
    user = request.user
    employee = get_object_or_404(Employee, user=user)

    # Check if the employee's position is either TL or Manager
    if employee.position.name not in ['Team Lead', 'Manager']:
        return render(request, 'no_access.html', {
            'message': 'You do not have permission to view this page.'
        })

    # Filter leave requests based on position
    if employee.position.name == 'Team Lead':
        leave_requests = LeaveRequest.objects.filter(
            status='Pending',
            tl=employee
        )
    elif employee.position.name == 'Manager':
        leave_requests = LeaveRequest.objects.filter(
            status='Pending',
            manager=None
        )

    if request.method == 'POST':
        form = LeaveApprovalForm(request.POST)
        leave_request_id = request.POST.get('leave_request_id')
        leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

        if form.is_valid():
            action = form.cleaned_data['action']
            if action == 'approve':
                if employee.position.name == 'Team Lead':
                    leave_request.status = 'Approved by Team Lead'
                    leave_request.manager = None  # Ensure the manager is not set
                elif employee.position.name == 'Manager':
                    leave_request.status = 'Approved by Manager'
            elif action == 'reject':
                leave_request.status = 'Rejected'
            leave_request.processed_on = timezone.now()
            leave_request.save()

            # Notify the requester
            messages.success(request, 'Leave request updated successfully!')
            return redirect('head_officers')

    else:
        form = LeaveApprovalForm()
    
    if employee.position.name == 'Team Lead':
        # Team Leads should only see leave requests assigned to them but not their own
        leave_requests = LeaveRequest.objects.filter(
            status='Pending',
            tl=employee
        ).exclude(employee=employee)  # Exclude requests submitted by the current Team Lead
    elif employee.position.name == 'Manager':
        # Managers should see all pending leave requests assigned to them
        leave_requests = LeaveRequest.objects.filter(
            status='Pending',
            manager=None  # Only see requests where no manager has been assigned
        )

    return render(request, 'main/head_officers.html', {
        'leave_requests': leave_requests,
        'form': form,
    })


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
                attendance.check_in_time = timezone.localtime().time()
                attendance.status = 'Present'
                attendance.save()
                employee.status = 'Active'
                employee.save()
                messages.success(request, 'You have successfully checked in.')

        elif 'check_out' in request.POST:
            if attendance.check_in_time is not None and attendance.check_out_time is None:
                attendance.check_out_time = timezone.localtime().time()

                # Calculate the duration of work
                check_in_datetime = datetime.combine(today, attendance.check_in_time)
                check_out_datetime = datetime.combine(today, attendance.check_out_time)
                duration = check_out_datetime - check_in_datetime

                # Check if the duration is at least 6 hours
                if duration >= timedelta(hours=6):
                    attendance.status = 'Present'
                else:
                    attendance.status = 'Absent'

                attendance.save()
                employee.status = 'Inactive'
                employee.save()
                messages.success(request, 'You have successfully checked out.')

        return redirect('attendance')

    # Determine the view type
    view_type = request.GET.get('view', 'table')
    
    # Get all attendance records for the current month
    attendance_records = Attendance.objects.filter(employee=employee, date__month=today.month).order_by('-date')

    # End-of-day check if the employee hasn't checked out
    if attendance.check_out_time is None and attendance.check_in_time is not None:
        check_in_datetime = datetime.combine(today, attendance.check_in_time)
        now = timezone.localtime().time()
        duration = datetime.combine(today, now) - check_in_datetime

        if duration >= timedelta(hours=6):
            attendance.status = 'Absent'
            messages.warning(request, 'You forgot to check out. Your status has been marked as absent.')
        else:
            attendance.status = 'Absent'

        attendance.save()

    return render(request, 'main/attendance.html', {
        'employee': employee,
        'attendance': attendance,
        'attendance_records': attendance_records,
        'view_type': view_type,
    })

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out Successfully")
    return redirect('login')

# def is_admin(user):
#     return user.is_superuser

# @user_passes_test(is_admin)
# def admin_view(request):
#     return render(request, 'main/admin_view.html')

# def is_manager(user):
#     return user.groups.filter(name='Manager').exists()

# def is_team_leader(user):
#     return user.groups.filter(name='Team Leader').exists()