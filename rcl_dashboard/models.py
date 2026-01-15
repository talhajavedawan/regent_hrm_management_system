
from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,blank=True,null=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    nationality = models.CharField(
        max_length=10,
        choices=[('INDIA', 'India'), ('UK', 'UK')]
    )
    share_code = models.CharField(max_length=20,blank=True,null=True)
    visa_status = models.CharField(
        max_length=20,
        choices=[('VALID', 'Valid'), ('EXPIRED', 'Expired')]
    )
    
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    def __str__(self):
        return self.name


class VisaExpiry(models.Model):
    name = models.CharField(max_length=100)
    share_code = models.CharField(max_length=20)
    expiry_date = models.DateField()

    def __str__(self):
        return self.share_code


class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reason = models.TextField()
    from_date = models.DateField()
    to_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[('PENDING','Pending'), ('APPROVED','Approved'), ('REJECTED','Rejected')],
        default='PENDING'
    )
    applied_on = models.DateTimeField(auto_now_add=True)


class SalarySlip(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    file = models.FileField(upload_to='salary_slips/')


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Notification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.message}"