from django.db import models
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, User
import datetime


# Create your models here.

def student_matricule_validator(value):
    pattern=  r'^UBa(1[0-9]|2[0-4])([A-Z]{2})(\d{3})$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid Matricule format. Please use the format UBaXXYYZZZ where XX is a number between 10-24, YY is are two letters and ZZZ is a number betwenn 001 - 999')

def lecturer_matricule_validator(value):
    pattern=r'^UBaLec(1[0-9]|2[0-4])([A-Z]{1})(\d{4})$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid Matricule format. Please contact admin for a valid matricule number')

class Schools(models.Model):
    name=models.CharField(blank=False, max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering=['name']
        
        
    
class Department(models.Model):
    name=models.CharField(blank=False, max_length=50, unique=True)
    school=models.ForeignKey(Schools , on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name + ' - ' + self.school.name
    class Meta:
        ordering=['name']
        

class User(AbstractUser):
    role_choice=(('student','Student'), ('lecturer','Lecturer'),)
    user_type=models.CharField(max_length=10, choices=role_choice)
    first_name=models.CharField(blank=False, max_length=100)
    last_name=models.CharField(blank=False, max_length=100)
    email=models.EmailField(blank=False, unique=True)
    phone=models.IntegerField(default='67000000')
    username=models.CharField(blank=False, max_length=50, unique=True)
    
    device_id = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name 
    
class Student(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type':'student'})
    matricule_number=models.CharField(blank=False, unique=True, validators=[student_matricule_validator], max_length=10)
    school=models.ForeignKey(Schools , on_delete=models.CASCADE)
    department=models.ForeignKey(Department, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' - ' +self.matricule_number
    
    class Meta:
        ordering=['matricule_number']
    
class Lecturer(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type':'lecturer'})
    matricule_number=models.CharField(blank=False, unique=True, validators=[lecturer_matricule_validator], max_length=13)
    
    
    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' - ' +self.matricule_number
    
    class Meta:
        ordering=['matricule_number']
    
class Course(models.Model):
    name=models.CharField(blank=False, max_length=100)
    
    department=models.ForeignKey(Department, on_delete=models.CASCADE)
    code=models.CharField(unique=True, max_length=50)
    def __str__(self):
        return self.name + ' - ' + self.department.name + ' - ' + self.department.school.name
    
class ClassSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    range_radius = models.FloatField(help_text="Allowed distance in meters", default=10.0)

    latitude=models.FloatField(default=1.0)
    longitude=models.FloatField(default=1.0)
    hall=models.CharField(blank=True, max_length=100)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be afte start time")
    
    def __str__(self):
        return self.course.name + ' - ' + self.course.department.name + ' - ' + self.course.department.school.name
    
    
    
    
class Attendance(models.Model):
    is_present=models.BooleanField(default=False)
    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance_time = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
            return self.student.matricule_number
    
    
        
    


    
    
    

    
