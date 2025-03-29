import dateutil
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from tello.models import StorySession, StudentReport, Teacher, Student
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
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
                # Redirect to student addition page
                return redirect("dashboard")
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


@login_required
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


@api_view(["POST"])
def create_story_session(request):
    """
    Expects JSON with:
      - student_id: ID of the student
      - story_id: Story identifier (not a FK)
      - start_time: ISO formatted datetime string
      - end_time: ISO formatted datetime string
    """
    data = request.data
    try:
        student_id = data["student_id"]
        story_id = data["story_id"]
        start_time = dateutil.parser.isoparse(data["start_time"])
        end_time = dateutil.parser.isoparse(data["end_time"])
    except KeyError:
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Invalid datetime format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    student = get_object_or_404(Student, pk=student_id)

    session = StorySession.objects.create(
        student=student,
        story_id=story_id,
        start_time=start_time,
        end_time=end_time
    )
    # The save() in StorySession will calculate the duration
    return Response({"message": "Session created", "session_id": session.id}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def create_student_report(request):
    """
    Expects JSON with:
      - session_id: ID of the StorySession
      - vocab_score: float
      - structure_sim_score: float
      - response_length: float
      - avg_engagement: float
      - final_score: float
      - prompt_interaction_ratio: float
      - prompt_interaction_count: int
      - feedback_notes: (optional) string
    """
    data = request.data
    try:
        session_id = data["session_id"]
        vocab_score = float(data["vocab_score"])
        structure_sim_score = float(data["structure_sim_score"])
        response_length = float(data["response_length"])
        avg_engagement = float(data["avg_engagement"])
        final_score = float(data["final_score"])
        prompt_interaction_ratio = float(data["prompt_interaction_ratio"])
        prompt_interaction_count = int(data["prompt_interaction_count"])
        feedback_notes = data.get("feedback_notes", "")

    except KeyError as e:
        return Response({"error": f"Missing required field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({"error": "Invalid data type in request"}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure StorySession exists
    story_session = get_object_or_404(StorySession, pk=session_id)

    # Create and save the StudentReport
    report = StudentReport.objects.create(
        story_session=story_session,
        vocab_score=vocab_score,
        structure_sim_score=structure_sim_score,
        response_length=response_length,
        avg_engagement=avg_engagement,
        final_score=final_score,
        prompt_interaction_ratio=prompt_interaction_ratio,
        prompt_interaction_count=prompt_interaction_count,
        feedback_notes=feedback_notes
    )

    return Response(
        {
            "message": "Student report created successfully",
            "report_id": report.id
        },
        status=status.HTTP_201_CREATED
    )


def add(request):
    return render(request, 'student_addition.html')


def report(request):
    return render(request, 'progress_report.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def report_list(request):
    reports = StudentReport.objects.select_related(
        'story_session__student').all()

    report_data = [
        {
            'id': report.id,
            'student_id': report.story_session.student.studentcode,
            'student_name': report.story_session.student.studentname,
            'created_at': report.created_at
        }
        for report in reports
    ]

    return render(request, 'report_list.html', {'reports': report_data})


def logout_teacher(request):
    """Logs out the user and redirects to the login page."""
    logout(request)
    return redirect('teacher_login')


@login_required
def report_detail(request, report_id):
    report = get_object_or_404(StudentReport, id=report_id)
    # Get all sessions for the student in chronological order.
    sessions = StorySession.objects.filter(student=report.story_session.student).order_by('date')
    
    # Create chart_data list: each item is a dict with date and final_score.
    chart_data = []
    for session in sessions:
        # Assuming there is one report per session; adjust if necessary.
        session_report = session.reports.first()
        if session_report:
            chart_data.append({
                'date': session.date.strftime("%Y-%m-%d"),
                'final_score': session_report.final_score,
            })

    return render(request, 'report_detail.html', {
        'report': report,
        'chart_data': chart_data,
    })
