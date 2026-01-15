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
            user = User.objects.create_user(
            username=name,
            password='emp123'
        )
            Employee.objects.create(
                user=user,
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


# ---------------- DOWNLOAD SALARY (EMPLOYEE) ----------------
@login_required
def salary_list(request):
    employee = Employee.objects.get(user=request.user)
    slips = SalarySlip.objects.filter(employee=employee)
    return render(request, 'employee/salary.html', {'slips': slips})


@login_required
def employee_dashboard(request):
    employee = Employee.objects.get(user=request.user)

    slips = SalarySlip.objects.filter(employee=employee)
    announcements = Announcement.objects.all().order_by('-created_at')[:5]
    notifications = Notification.objects.filter(employee=employee, is_read=False)
    notifications_count = notifications.count()
    
    leave_count = Leave.objects.filter(employee=employee).count()
    salary_count = SalarySlip.objects.filter(employee=employee).count()
    unread_count = Notification.objects.filter(
        employee=employee,
        is_read=False
    ).count()


    return render(request, 'employee/dashboard.html', {
        'employee': employee,
        'slips': slips,
        'announcements': announcements,
        'notifications': notifications,
        'notifications_count':notifications_count,
        'leave_count': leave_count,
        'unread_count': unread_count,
        'salary_count': salary_count
    })

@login_required
def hr_dashboard(request):
    return render(request, 'hr/dashboard.html', {
        'employees': Employee.objects.all(),
        'pending_leaves': Leave.objects.filter(status='PENDING'),
        'salaries': SalarySlip.objects.all()
    })



def logout_view(request):
    logout(request)
    return render(request, 'logout.html')

@login_required
def employee_list(request):
    employees = Employee.objects.all()
    visa_map = {
        v.share_code: v.expiry_date
        for v in VisaExpiry.objects.all()
    }
    return render(request, 'hr/employee_list.html', {
       # 'employees': employees,
       'employees':employees,
        'visa_map': visa_map
       # 'visadate':visadate
    })

@login_required
def edit_employee(request, id):
    emp = Employee.objects.get(id=id)

    if request.method == 'POST':
        emp.name = request.POST['name']
        emp.department = request.POST['department']
       # emp.nationality = request.POST['nationality']
        emp.save()
        return redirect('employee_list')

    return render(request, 'hr/edit_employee.html', {'emp': emp})


@login_required
def delete_employee(request, id):
    employee =get_object_or_404(Employee,id = id)
    emp = Employee.objects.get(id=id)
    if employee.nationality == 'United Kingdom':
        employee.delete()
        emp.user.delete()   # deletes linked auth user
        emp.delete()
        return redirect('employee_list')
    if employee.nationality != 'United Kingdom':
        employee.delete()
        emp.user.delete()
        emp.delete()
        return redirect('employee_list')
    
   
    
    return redirect('employee_list')


from django.shortcuts import render, redirect
from .models import Employee, SalarySlip

def upload_salary_slip(request):
    employees = Employee.objects.all()

    if request.method == 'POST':
        emp_id = request.POST['employee']
        month = request.POST['month']
        file = request.FILES['file']

        employee = Employee.objects.get(id=emp_id)

        SalarySlip.objects.create(
            employee=employee,
            month=month,
            file=file
        )
        return redirect('/hr/dashboard/')

    return render(request, 'hr/upload_salary_slip.html', {
        'employees': employees
    })


def view_salary_slips(request):
    employee = Employee.objects.get(share_code=request.user.username)
    slips = SalarySlip.objects.filter(employee=employee)

    return render(request, 'employee/salary_slips.html', {
        'slips': slips
    })



def create_announcement(request):
    if request.method == 'POST':
        title = request.POST['title']
        message = request.POST['message']

        Announcement.objects.create(
            title=title,
            message=message
        )
        return redirect('/hr/dashboard/')

    return render(request, 'hr/create_announcement.html')


@login_required
def employee_profile_view(request):
    """
    Displays full employee profile details (read-only)
    """
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return render(request, 'common/error.html', {
            'message': 'Employee profile not found.'
        })

    return render(request, 'employee/profile_view.html', {
        'employee': employee
    })
    
@login_required
def employee_profile_edit(request):
    """
    Allows employee to update email, mobile and photo
    """
    employee = Employee.objects.get(user=request.user)

    if request.method == 'POST':
        employee.email = request.POST.get('email')
        employee.mobile = request.POST.get('mobile')

        if request.FILES.get('photo'):
            employee.photo = request.FILES['photo']

        employee.save()
        return redirect('employee_profile_view')

    return render(request, 'employee/profile.html', {
        'employee': employee
    })