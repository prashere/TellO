from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_login, name='teacher_login'),
    path("api/teacher-login/", views.teacher_login_api, name="teacher_login_api"),
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    path('add/', views.add_student, name='add'),
    path('report/', views.report, name='home'),
    path("api/get-students/<int:teacher_id>/",
         views.get_students_for_teacher, name="get_students_for_teacher"),
]
