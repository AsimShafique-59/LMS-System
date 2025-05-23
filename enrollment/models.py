from django.conf import settings
# from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

# User = get_user_model()

class User(AbstractUser):
    # age = models.PositiveIntegerField(null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    # enrolled_date = models.DateField(auto_now_add=True)
    role = models.CharField(
        max_length=50,
        choices=[("student", "Student"), ("teacher", "Teacher")],
        null=True,
        blank=True
    )
class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='students')

    # roll_no = models.CharField(max_length=50)

class Staff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff')

class Subject(models.Model):
    name = models.CharField(max_length=100)
    credit_hours = models.PositiveIntegerField()
    grade = models.CharField(max_length=2, blank=True, null=True)

class Enrollment(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='enrollments')
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name='enrollments')



