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
