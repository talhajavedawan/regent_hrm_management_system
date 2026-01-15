from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', home_page,name="home_page"),
    path('hr/login/', hr_login),
    path('employee/login/', employee_login),

    # path('hr/add-employee/', add_employee, name='add_employee'),
    path('employee/apply-leave/', apply_leave),
    # path('hr/approve-leave/<int:id>/', approve_leave),
    path('hr/leave-approvals/', hr_leave_approve_list),
    path('hr/approve/<int:leave_id>/', approve_leave),
    path('hr/reject/<int:leave_id>/', reject_leave),
   path('hr/upload-salary/', upload_salary_slip),
    path('employee/salary-slips/', view_salary_slips),

    path('employee/dashboard/', employee_dashboard,name="employee_dashboard"),
    path('hr/dashboard/', hr_dashboard,name="hr_dashboard"),
    path('logout/', logout_view, name='logout'),
    path('hr/employees/', employee_list, name='employee_list'),
    path('hr/add-employee/', add_employee,name="add_employee"),
    path('hr/edit-employee/<int:id>/', edit_employee),
    path('hr/delete-employee/<int:id>/', delete_employee),
    path('hr/announcement/', create_announcement),
# path('employee/profile/', employee_profile),
    path('employee/profile/', employee_profile_view, name='employee_profile_view'),
    path('employee/profile/edit/', employee_profile_edit, name='employee_profile_edit'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)