from django.shortcuts import render, redirect
from .models import User, Student, Lecturer, Schools, Department, Course, ClassSession, Attendance
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count, Q, F, FloatField, ExpressionWrapper, Case, When
import re

# Create your views here.

#statics calculations

#get name abbreviations
def get_name_abb(first_name, last_name):
    if not first_name or not last_name:
        return 'AU'
    return first_name[0].upper() + last_name[0].upper()

#get name attendance review
def get_att_rev(att):
    if att<=25:
        return 'POOR'
    elif att<=50:
        return 'FAIR'
    elif att<=75:
        return 'FAIRLY GOOD'
    elif att<=90:
        return 'GOOD'
    else:
        return 'EXCELLENT'
    
#get attandance progress bar limit
def get_att_bar(att):
    if att<=25:
        return 'red'
    elif att<=50:
        return '#f59e0b'
    elif att<=75:
        return 'blue'
    elif att<=90:
        return 'orange'
    else:
        return ' #10b981'

def index(request):
    return render(request, 'index.html')

def createstudent(request):
        if request.user.is_authenticated:
            if request.user.user_type == 'student':
                return redirect('student-dashboard')
            else:
                return redirect('lecturer-dashboard')
    
        schools=Schools.objects.all()
        if request.method == 'POST':
            first_name=request.POST.get('first-name')
            last_name=request.POST.get('last-name')
            username=request.POST.get('username')
            email=request.POST.get('email')
            phone=request.POST.get('phone')
            password=request.POST.get('password')
            user_type='student'
            matricule_number=request.POST.get('matricule_number')
            school_id=request.POST.get('school')
            department_id=request.POST.get('department')
            school=Schools.objects.get(id=school_id)
            department=Department.objects.get(id=department_id)
            
            try:
                if User.objects.filter(username=username, phone=phone, email=email).exists():
                    messages.error(request, 'Username, Phone number, or Email already exists')
                    return redirect('create-student')
                else:
                   
                    
                    pattern=  r'^UBa(1[0-9]|2[0-4])([A-Z]{2})(\d{3})$'
                    if not re.match(pattern, matricule_number):
                        messages.error(request, 'Invalid Matricule format. Please use the format UBaXXYYZZZ where XX is a number between 10-24, YY is are two letters and ZZZ is a number betwenn 001 - 999')
                        return redirect('create-student')
                    else:
                        try:
                            user=User.objects.create_user(username=username, password=password, email=email, phone=phone, first_name=first_name, last_name=last_name, user_type=user_type)
                        except  IntegrityError:
                            messages.error(request, 'Username, Phone number, or Email already exists')
                            return redirect('create-student')
                        Student.objects.create(
                            user=user,
                            matricule_number=matricule_number,
                            school=school,
                            department=department
                            
                        )
                        login(request, user)
                        messages.success(request,'Account Created')
                        return redirect('create-student')
            except (ValidationError or IntegrityError )as e:
                messages.error(request, e)
    
    
        context={
            'schools':schools,
        }
        return render(request, 'signup.html', context)
    
def createLecturer(request):
        if request.user.is_authenticated:
            if request.user.user_type == 'lecturer':
                return redirect('lecturer-dashboard')
            else:
                return redirect('student-dashboard')
    
    
        schools=Schools.objects.all()
        if request.method == 'POST':
            first_name=request.POST.get('first-name')
            last_name=request.POST.get('last-name')
            username=request.POST.get('username')
            email=request.POST.get('email')
            phone=request.POST.get('phone')
            password=request.POST.get('password')
            user_type='lecturer'
            matricule_number=request.POST.get('matricule_number')
            
            
            try:
                if User.objects.filter(username=username, phone=phone, email=email).exists():
                    messages.error(request, 'Username, Phone number, or Email already exists')
                    return redirect('create-lecturer')
                else:
  
                    pattern=r'^UBaLec(1[0-9]|2[0-4])([A-Z]{1})(\d{4})$'
                    if not re.match(pattern, matricule_number):
                            messages.error(request, 'Invalid Matricule format. Please contact admin for a valid matricule number')
                            return redirect('create-lecturer')
                    else:
                        try:
                            user=User.objects.create_user(username=username, password=password, email=email, phone=phone, first_name=first_name, last_name=last_name, user_type=user_type)
                        except IntegrityError :
                            messages.error(request, 'Username, Phone number, or Email already exists')
                            return redirect('create-lecturer')
                        Lecturer.objects.create(
                            user=user,
                            matricule_number=matricule_number,    
                        )
                    
                        login(request, user)
                        messages.success(request,'Account Created')
                        return redirect('lecturer-dashboard')
            except (ValidationError or IntegrityError) as e:
                messages.error(request, 'Username, Phone number, or Email already exists')
    
    
        context={
            'schools':schools,
        }
        return render(request, 'signup.html', context)
    
def user_login(request):
    
    if request.method == 'POST':       
        username=request.POST.get('username')   
        password=request.POST.get('password')
        
        try:
            User.objects.get(username=username)
        except:
            messages.error(request, 'Username not found')
        user=authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if user.user_type=='student':
                return redirect('student-dashboard')
            elif user.user_type=='lecturer':
                return redirect('lecturer-dashboard')
            messages.success(request, 'Welcome back')
        else:
            messages.error('Inavlid Creditials')
            return redirect('login-user')
            
    return render(request, 'login.html')

def user_logout(requeest):
    logout(requeest)
    return redirect('login')
            
            
    
    
        
    
def getdepartments(request):
    school_id=request.GET.get('school_id')
    departments=Department.objects.filter(school_id=school_id)
    data=[{'id':department.id, 'name':department.name} for department in departments]
    return JsonResponse(data, safe=False)

def lecturerDasboard(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'lecturer':
            lecturer=Lecturer.objects.get(user=request.user)
            class_sesions=ClassSession.objects.filter(lecturer=lecturer)
            total_class_session=class_sesions.count()
            context={
                'class_sessions':class_sesions,
                'total_class_session': total_class_session,
            }
            
            
            return render(request, 'lecturer-dashboard.html', context)
        else:
            return redirect('student-dashboard')
        
def studentDashboard(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'student':
            
            student=Student.objects.get(user=request.user)
            attendance=Attendance.objects.filter(student=student)
            class_sessions_attendance=ClassSession.objects.annotate(total_attendance=Count('attendances'))
            
            #attendance stattistic
            attendance_count=attendance.count()
            attendance_present=Attendance.objects.filter(student=student, is_present=True, class_session__course__department=student.department).count()
            attendance_absent=Attendance.objects.filter(student=student, is_present=False).count()
            attendance_percentage=(attendance_present/10)*100
            
            
            class_sessions=ClassSession.objects.filter(
                course__department=student.department
                ).annotate(
                    total_attendance=Count('attendances'),
                    present_attendance=Count('attendances', filter=Q(attendances__is_present=True)),
                    
                    
                ).annotate(class_session_percentage=Case( 
                When(total_attendance=0, then=0),
                default=ExpressionWrapper(F('present_attendance')*100.0 / F('total_attendance'),
                output_field=FloatField()), output_field=FloatField(), ),
                )
                
            for class_session in class_sessions:
                class_session.bar=get_att_bar(class_session.class_session_percentage)
                
            
            
            name_abb=get_name_abb(request.user.first_name, request.user.last_name)
            attendance_review=get_att_rev(attendance_percentage)
            
            
            context={
                'student':student,
                'name_abb':name_abb,
                'attendance':attendance,
                'attendance_count':attendance_count,
                'attendance_percentage':attendance_percentage,
                'attendance_absent':attendance_absent,
                'attendance_present':attendance_present,
                'attendance_review':attendance_review,
                'class_sessions':class_sessions,
                'class_sessions_count':class_sessions.count()
            }
            return render(request, 'student-dashboard.html', context)
        else:
            return redirect('lecturer-dashboard')
    
        
            
        
        
    
    