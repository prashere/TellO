from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_login, name='teacher_login'),
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    path('add/', views.add_student, name='add'),
    path('report/', views.report, name='home'),

]
