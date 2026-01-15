from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import date
from .models import *
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from .models import Announcement, Notification, Leave
from django.utils import timezone

from .models import Employee, VisaExpiry
from django.shortcuts import render, redirect

def home_page(request):
    return render(request, 'home.html')
# ---------------- HR LOGIN ----------------
def hr_login(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user and user.is_staff:
            login(request, user)
            return redirect('hr_dashboard')
    return render(request, 'hr/login.html')
# ---------------- EMPLOYEE LOGIN ----------------
def employee_login(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user and not user.is_staff:
            login(request, user)
            return redirect('employee_dashboard')
    return render(request, 'employee/login.html')


# ---------------- ADD EMPLOYEE (HR) ----------------


@login_required
def add_employee(request):
    if request.method == 'POST':
        name = request.POST['name']
        department = request.POST['department']
        nationality = request.POST['nationality']
        share_code = request.POST.get('share_code')

        # 🇬🇧 UK employee → skip visa check
        if nationality == 'United Kingdom':
            Employee.objects.create(
                name=name,
                department=department,
                nationality=nationality,
                visa_status='VALID',
                share_code="Not Required"
            )
            print("hello")
            return redirect('/hr/employees/')

        # 🌍 Non-UK → Share code mandatory
        if not share_code:
            return render(request, 'hr/error.html', {
                'msg': 'Share code is required for non-UK employees.'
            })

        # Check visa using share code
        try:
            visa = VisaExpiry.objects.get(share_code=share_code)
        except VisaExpiry.DoesNotExist:
            return render(request, 'hr/error.html', {
                'msg': 'Invalid share code. Visa record not found.'
            })

        # Check expiry

        if visa.expiry_date < timezone.now().date():
            return render(request, 'hr/error.html', {
                'msg': 'Visa is expired. Employee cannot be added.'
            })
        user = User.objects.create_user(
            username=name,
            password='emp123'
        )

        # Valid visa → add employee
        Employee.objects.create(
             user=user,
            name=name,
            department=department,
            nationality=nationality,
            share_code=share_code,
            visa_status='VALID'
        )

        return redirect('/hr/employees/')

    return render(request, 'hr/add_employee.html')
# ---------------- APPLY LEAVE (EMPLOYEE) ----------------
@login_required
def apply_leave(request):
    employee = Employee.objects.get(user=request.user)

    if request.method == 'POST':
        Leave.objects.create(
            employee=employee,
            reason=request.POST['reason'],
            from_date=request.POST['from_date'],
            to_date=request.POST['to_date']
        )
        return redirect('employee_dashboard')

    return render(request, 'employee/apply_leave.html')


# ---------------- APPROVE LEAVE (HR) ----------------
@login_required
def approve_leave(request, leave_id):
    leave = Leave.objects.get(id=leave_id)
    print(leave)    
    leave.status = 'APPROVED'
    leave.save()
    Notification.objects.create(
        employee=leave.employee,
        message="Your leave request has been APPROVED."
    )

    return redirect('/hr/leave-approvals/')

def hr_leave_approve_list(request):
    leaves = Leave.objects.all().order_by('-applied_on')
    return render(request, 'hr/approve_leave.html', {'leaves': leaves})


def reject_leave(request, leave_id):
    leave = Leave.objects.get(id=leave_id)
    leave.status = 'Rejected'
    leave.save()
    Notification.objects.create(
        employee=leave.employee,
        message="Your leave request has been REJECTED."
    )

    return redirect('/hr/leave-approvals/')
# ---------------- UPLOAD SALARY (HR) ----------------
@login_required
def upload_salary(request):
    if request.method == 'POST':
        SalarySlip.objects.create(
            employee_id=request.POST['employee'],
            month=request.POST['month'],
            file=request.FILES['file']
        )
        return redirect('upload_salary')

    return render(request, 'hr/upload_salary.html', {
        'employees': Employee.objects.all()
    })
