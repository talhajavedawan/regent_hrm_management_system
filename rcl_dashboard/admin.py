from django.contrib import admin

# Register your models here.
from  .models import Employee,VisaExpiry,SalarySlip,Leave

admin.site.register(Employee)
admin.site.register(VisaExpiry)
admin.site.register(SalarySlip)
admin.site.register(Leave)
