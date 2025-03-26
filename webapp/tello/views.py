from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from tello.models import Teacher, Student
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status


# Create your views here.
def teacher_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # Authenticate using Django's built-in system
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if the user is a teacher
            if hasattr(user, "teacher"):  # Ensure this user has a related Teacher profile
                login(request, user)  # Log in the user
                # Store teacher ID in session
                request.session["teacher_id"] = user.teacher.teacherid
                messages.success(request, "Login successful!")
                return redirect("add")  # Redirect to student addition page
            else:
                messages.error(request, "You are not registered as a teacher.")
        else:
            messages.error(
                request, "Invalid username or password. Please try again.")

    return render(request, "login.html")  # Render login page again if failed


@api_view(['POST'])
def teacher_login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        if hasattr(user, "teacher"):  # Check if user has a teacher profile
            return Response({
                "message": "Login successful",
                "teacher_id": user.teacher.teacherid
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You are not registered as a teacher."}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({"message": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)


@login_required
def add_student(request):
    if request.method == "POST":
        student_name = request.POST.get("student_name")
        student_age = request.POST.get("student_age")
        student_code = request.POST.get("student_code")
        student_grade = request.POST.get("student_grade")
        student_notes = request.POST.get("student_notes", "")

        if student_name and student_age and student_grade:
            student = Student.objects.create(
                studentname=student_name,
                studentage=int(student_age),
                studentcode=student_code,
                studentgrade=student_grade,
                additional_notes=student_notes,
                # Link the student to the logged-in teacher
                assignedteacher=request.user.teacher,
            )
            student.save()
            messages.success(request, "Student added successfully!")
            return redirect("dashboard")  # Redirect to dashboard after success
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, "student_addition.html")


def teacher_dashboard(request):
    students = Student.objects.all()  # Fetch all students from DB
    return render(request, "dashboard.html", {"students": students})


@api_view(["GET"])
def get_students_for_teacher(request, teacher_id):
    """API to fetch students assigned to a specific teacher"""
    teacher = get_object_or_404(Teacher, teacherid=teacher_id)
    students = Student.objects.filter(
        assignedteacher=teacher).values("studentid", "studentname")

    return Response({"students": list(students)}, status=status.HTTP_200_OK)


# def login(request):
#     return render(request, 'login.html')


def add(request):
    return render(request, 'student_addition.html')


def report(request):
    return render(request, 'progress_report.html')


def dashboard(request):
    return render(request, 'dashboard.html')
