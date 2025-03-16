from django.shortcuts import render

# Create your views here.


def login(request):
    return render(request, 'login.html')


def add(request):
    return render(request, 'student_addition.html')


def report(request):
    return render(request, 'progress_report.html')


def dashboard(request):
    return render(request, 'dashboard.html')
