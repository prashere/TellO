from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacherid = models.AutoField(primary_key=True)
    teachername = models.CharField(max_length=100)
    teachergrade = models.CharField(max_length=50)

    def __str__(self):
        return self.teachername


class Student(models.Model):
    studentid = models.AutoField(primary_key=True)
    studentcode = models.CharField(max_length=4, unique=True)
    studentname = models.CharField(max_length=100)
    studentgrade = models.CharField(max_length=50)
    studentage = models.IntegerField()
    assignedteacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    additional_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.studentname
