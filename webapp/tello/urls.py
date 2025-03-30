from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_login, name='teacher_login'),
    path("api/teacher-login/", views.teacher_login_api, name="teacher_login_api"),
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    path('add/', views.add_student, name='add'),
    path('report/', views.report, name='home'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path("api/get-students/<int:teacher_id>/",
         views.get_students_for_teacher, name="get_students_for_teacher"),
    path("api/create-story-session/", views.create_story_session,
         name="create_story_session"),
    path("api/create-student-report/", views.create_student_report,
         name="create_student_report"),
    path("report_list/", views.report_list, name="report_list"),
    path('logout/', views.logout_teacher, name='logout'),
    path('api/add-student-vocabulary/', views.add_student_vocabulary,
         name='add_student_vocabulary'),
]
