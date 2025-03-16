from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='home'),
    path('dashboard/', views.dashboard, name='home'),
    path('add/', views.add, name='home'),
    path('report/', views.report, name='home'),

]
