from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', home_page,name="home_page"),
    path('hr/login/', hr_login),
]