from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serilizers import (
    RegisterStudentSerializer,
    RegisterLecturerSerializer,
    ClassSessionSerializer,
    AttendanceSerializer,
    GetStudents,
    UserSerializer,
    LoginSerializer,
    ClassSessionAttendanceSerializer
)

from rest_framework.pagination import PageNumberPagination
from base.models import User, Student, Lecturer, Schools, Department, Course, ClassSession, Attendance
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Count, Q, F, FloatField, ExpressionWrapper, Case, When, Sum, Avg
from datetime import datetime
import math
from django.utils import timezone




# Helper function for generating JWT tokens
def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class SessionProximityCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            student_lat = float(request.data.get("student_latitude"))
            student_lon = float(request.data.get("student_longitude"))
        except (TypeError, ValueError):
            return Response({"error": "Invalid or missing coordinates"}, status=400)

        session_id = request.data.get("session_id")
        if not session_id:
            return Response({"error": "Missing session_id"}, status=400)

        try:
            session = ClassSession.objects.get(id=session_id)
        except ClassSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=404)

        # Lecturer’s location at session creation is the center
        center_lat = session.latitude
        center_lon = session.longitude

        # Approximate conversion: 1 degree ≈ 111,000 meters
        meters_per_degree = 111000

        lat_diff = abs(center_lat - student_lat) * meters_per_degree
        lon_diff = abs(center_lon - student_lon) * meters_per_degree * math.cos(math.radians(center_lat))

        within_square = lat_diff <= 5 and lon_diff <= 5  # within 10x10 meter square

        return Response({
            "access_granted": within_square,
            "lat_diff_meters": round(lat_diff, 2),
            "lon_diff_meters": round(lon_diff, 2),
            "message": "Access granted" if within_square else "Access denied: too far from class location"
        })



# Create a student
class StudentRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterStudentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.create_user(
                    username=serializer.validated_data["username"],
                    first_name=serializer.validated_data["first_name"],
                    last_name=serializer.validated_data["last_name"],
                    phone=serializer.validated_data["phone"],
                    email=serializer.validated_data["email"],
                    password=serializer.validated_data["password"],
                    user_type="student",
                )
                Student.objects.create(
                    user=user,
                    school=Schools.objects.get(name=serializer.validated_data["school_name"]),
                    department=Department.objects.get(name=serializer.validated_data["department_name"]),
                    matricule_number=serializer.validated_data["matricule_number"],
                )
                tokens = generate_tokens(user)
                login(request, user)
                return Response(
                    {"message": "Student registered successfully", "tokens": tokens},
                    status=status.HTTP_201_CREATED,
                )
            except ObjectDoesNotExist as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create a lecturer
class LecturerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterLecturerSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.create_user(
                    username=serializer.validated_data["username"],
                    first_name=serializer.validated_data["first_name"],
                    last_name=serializer.validated_data["last_name"],
                    phone=serializer.validated_data["phone"],
                    email=serializer.validated_data["email"],
                    password=serializer.validated_data["password"],
                    user_type="lecturer",
                )
                Lecturer.objects.create(
                    user=user,
                    matricule_number=serializer.validated_data["matricule_number"],
                )
                tokens = generate_tokens(user)
                login(request, user)
                return Response(
                    {"message": "Lecturer registered successfully", "tokens": tokens},
                    status=status.HTTP_201_CREATED,
                )
            except ObjectDoesNotExist as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User authentication


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                User.objects.get(username=serializer.validated_data["username"])
            except:
                return Response({"error": "User does not exists"}, status=status.HTTP_401_UNAUTHORIZED)
            user = authenticate(username=serializer.validated_data["username"], password=serializer.validated_data["password"])
            if user:
                tokens = generate_tokens(user)
                login(request, user)
                return Response(
                    {"message": "Logged in successfully", "tokens": tokens},
                    status=status.HTTP_200_OK,
                )
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Protected route
class ProtectedRoute(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Welcome, {request.user.username}"}, status=status.HTTP_200_OK)

#students dashboard
# Get all class sessions for a student
class StudentClassSessionView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)

            
            attendance=Attendance.objects.filter(student=student)
            class_sessions_attendance=ClassSession.objects.annotate(total_attendance=Count('attendances'))
            
            #attendance stattistic
            attendance_count=attendance.count()
            attendance_present=Attendance.objects.filter(student=student, is_present=True, class_session__course__department=student.department).count()
            attendance_absent=Attendance.objects.filter(student=student, is_present=False).count()
            att_arr=[]
            for att in attendance:
                att_arr.append({
                    "class_session": att.class_session.course.name,
                    "code":att.class_session.course.code,
                    "hall":att.class_session.hall,
                    "date": att.attendance_time,
                    "status":att.is_present,
                    
                    
                })
                
            current_time=datetime.now()

            
            class_sessions_mark=ClassSession.objects.filter(course__department=student.department, end_time__gte=current_time)
            upcoming_class_sessions=ClassSession.objects.filter(course__department=student.department, attendances__isnull=True, start_time__gte=current_time)
            class_sessions_to_mark = class_sessions_mark.exclude(attendances__student=student)
            upcoming=[{session.course.name} for session in upcoming_class_sessions]
            
            
            results_to_mark=[{'id':session.id, 'course':session.course.name, 'lecturer':session.lecturer.user.first_name + ' '+session.lecturer.user.last_name, 'date':session.start_time, 'end':session.end_time, 'hall':session.hall, "code":session.course.code, } for session in class_sessions_to_mark]
            
                
            
            #course attendance list, filter the course class session for a student using the student department
            #return also the total attendance, present attendance and class session percentage of the class sesion of that department
            class_sessions=ClassSession.objects.filter(
                course__department=student.department
                ).annotate(
                    total_attendance=Count('attendances'),
                    present_attendance=Count('attendances', filter=Q(attendances__is_present=True)),
                    
                    
                ).annotate(class_session_percentage=Case( 
                When(total_attendance=0, then=0),
                default=ExpressionWrapper(F('present_attendance')*100.0 / F('total_attendance'),
                output_field=FloatField()), output_field=FloatField(), ),
                ).order_by('-start_time')
            results=[{'id':session.id, 'attendance':round(session.class_session_percentage, 2), 'course':session.course.name, 'lecturer':session.lecturer.user.first_name + ' '+session.lecturer.user.last_name } for session in class_sessions]
            
            serializer = ClassSessionAttendanceSerializer(class_sessions, many=True)
            if class_sessions.count() == 0:
                attendance_percentage = 0
            else:
                attendance_percentage=(attendance_present/class_sessions.count())*100
            return Response({
                'student': f"{student.user.first_name} {student.user.last_name}",
                'matricule':student.matricule_number,
                'school': student.school.name,
                'department': student.department.name,
                'sessions': [{"data": serializer.data}],
                'upcoming':upcoming,
                'results':results,
                'attendance':att_arr,
                'attendance_count':attendance_count,
                'attendance_percentage':round(attendance_percentage, 2),
                'attendance_absent':attendance_absent,
                'attendance_present':attendance_present,
                'class_session_att':results_to_mark,
                
                'class_sessions_count':class_sessions.count()
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

#Mark attendance of an ongoing class class session course
# Fix Attendance marking
class AttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            class_session = ClassSession.objects.get(id=pk)
        except ClassSession.DoesNotExist:
            return Response({"message": "Class session not found"}, status=status.HTTP_404_NOT_FOUND)
        
        attendance, created = Attendance.objects.get_or_create(
            class_session=class_session,
            student=student,
            defaults={
                'is_present': True,
                'attendance_time': datetime.now()
            }
        )
        
        if created:
            return Response({'message': 'Attendance marked successfully'})
        else:
            return Response({'message': 'Attendance already marked'}, status=status.HTTP_400_BAD_REQUEST)
#get a class session
class GetClassSession(APIView):
    def get(self, request, pk):
        try:
            class_session = ClassSession.objects.get(id=pk)
            context = {
                'course': class_session.course.name,
                'id': class_session.id,
                'duration':class_session.duration_time,
                'lecturer': f"{class_session.lecturer.user.first_name} {class_session.lecturer.user.last_name}",
                'level': class_session.level,
            }
            return Response({'data': [context]}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Class session not found'}, status=status.HTTP_404_NOT_FOUND)





# Get all students in a department of a school
class GetDepartmentStudents(APIView):
    permission_classes = [IsAuthenticated]
    

    def get(self, request, pks, pkd):
        try:
            school = Schools.objects.get(id=pks)
            department = Department.objects.get(id=pkd, school=school)
            students = Student.objects.filter(school=school, department=department)
            serializer = GetStudents(students, many=True)
            return Response(
                {
                    "school": school.name,
                    "department": department.name,
                    "students": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            return Response({"error": "School or Department not found"}, status=status.HTTP_404_NOT_FOUND)


# Create class sessions





class LecturerClassSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ClassSessionSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                lecturer = Lecturer.objects.get(user=request.user)
                course = Course.objects.get(name=serializer.validated_data['course'])

                # Parse and make datetime aware
                start_time = datetime.fromisoformat(request.data['start_time'])
                end_time = datetime.fromisoformat(request.data['end_time'])

                if timezone.is_naive(start_time):
                    start_time = timezone.make_aware(start_time)
                if timezone.is_naive(end_time):
                    end_time = timezone.make_aware(end_time)

                # Save only fixed values — not serializer's original naive datetimes
                class_session = ClassSession.objects.create(
                    course=course,
                    lecturer=lecturer,
                    start_time=start_time,
                    end_time=end_time,
                    hall=serializer.validated_data['hall'],
                    latitude=serializer.validated_data['latitude'],
                    longitude=serializer.validated_data['longitude'],
                )

                return Response(
                    {"message": "Class session created successfully"},
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                return Response({'error': str(e)}, status=400)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LecturerClassSessionUpdateView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, pk):
        try:
            course=Course.objects.get(id=pk)
            class_sessions=ClassSession.objects.filter(course=course)
            serializer=ClassSessionSerializer(class_sessions, many=True)
            return Response({'data':serializer.data}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'course or class session does not found'}, status=status.HTTP_404_NOT_FOUND)
        




        

class GetStudentsAttendance(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request, pk):
        try:
            class_session = ClassSession.objects.get(id=pk)
            student = Attendance.objects.filter(class_session=class_session, is_present=True)
            serializer=AttendanceSerializer(student, many=True)
            return Response({'attendance': serializer.data, 'course':class_session.course.name})
        except ObjectDoesNotExist:
            return Response({'error': 'Class session  not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        
        


#Get all available schools
class SchoolView(APIView):
    
    def get(self, request):
        schools=Schools.objects.all()
        paginator=PageNumberPagination()
        paginator.page_size=10
        result_page=paginator.paginate_queryset(schools, request)
        data=[]
        for school in schools:
            school_data={
                'name':school.name,
                'id':school.id,
                'departments':[]
            }
            departments=Department.objects.filter(school=school)
            for department in departments:
                department_data={
                    'name':department.name,
                    'courses':[]
                }
                courses=Course.objects.filter(department=department)
                for course in courses:
                    course_data={
                        'name':course.name,
                        'code':course.code
                    }
                    department_data['courses'].append(course_data)
                school_data['departments'].append(department_data)
            data.append(school_data)
                    
        return paginator.get_paginated_response(data)

#Get all available departments
class DepartmentView(APIView):
    def get(self, request, school_name):
        try:
            
            departments=Department.objects.filter(school__name=school_name)
            return Response({'School':school_name, 'Departments':[{'id':department.id, 'name':department.name} for department in departments]})
        except Schools.DoesNotExist:
            return Response({'error':'School not found'}, status=status.HTTP_404_NOT_FOUND)
        
#Get all available Course in a schools departments
class CourseView(APIView):
    def get(self, request, pk):
        try:
            department=Department.objects.get(id=pk)
            courses=Course.objects.filter(department=department)
            
            return Response({'name':department.name, 'Courses':[{'id':course.id, 'name':course.name} for course in courses] } )
        except Department.DoesNotExist:
            return Response({'error':' Department not found'}, status=status.HTTP_404_NOT_FOUND)
       



class GetUserData(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        
        
        try:
            
            user = request.user
            
            return Response({
                'user': [{
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type,
                    'user_id':user.id,
                    'email':user.email,
                    'phone': user.phone
                }]
            })

        except ObjectDoesNotExist:
            return Response({'error': 'User does not exist'}, status=404)
        
#logout users
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token
            logout(request)
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Lecturer access to past class session attendance
class LecturerPastAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        lecturer = Lecturer.objects.get(user=request.user)
        try:
            lecturer = lecturer
            class_sessions = ClassSession.objects.filter(lecturer=lecturer, course__id=pk)
            attendance_data = []
            for session in class_sessions:
                attendance = Attendance.objects.filter(class_session=session, is_present=True)
                attendance_data.append({
                    "class_session": session.id,
                    "course": session.course.name,
                    "date": session.start_time,
                    "attendance": AttendanceSerializer(attendance, many=True).data,
                })
            return Response({"data": attendance_data}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "Lecturer or course not found"}, status=status.HTTP_404_NOT_FOUND)

class LecturerViewAllClassSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            lecturer = Lecturer.objects.get(user=request.user)

            class_sessions = ClassSession.objects.filter(lecturer=lecturer).annotate(
                total_attendance=Count('attendances'),
                present_attendance=Count('attendances', filter=Q(attendances__is_present=True)),
                class_session_percentage=Case(
                    When(total_attendance=0, then=0.0),
                    default=ExpressionWrapper(
                        F('present_attendance') * 100.0 / F('total_attendance'),
                        output_field=FloatField()
                    ),
                    output_field=FloatField()
                )
            )

            avg_att = class_sessions.aggregate(avg=Avg('class_session_percentage'))['avg'] or 0.0
            class_sessions_count = class_sessions.count()

            results = [
                {
                    'id': session.id,
                    'attendance': round(session.class_session_percentage or 0, 2),
                    'course_code': session.course.code,
                    'course': session.course.name,
                    'lecturer': f"{session.lecturer.user.first_name} {session.lecturer.user.last_name}",
                    'total_students': session.total_attendance,
                    'students_present': session.present_attendance,
                    'start': session.start_time,
                    'end': session.end_time,
                    'hall': session.hall
                }
                for session in class_sessions
            ]

            attendance_data = []
            for session in class_sessions:
                attendance = Attendance.objects.filter(class_session=session)
                attendance_data.append({
                    "class_session": session.id,
                    "course": session.course.name,
                    "course_code": session.course.code,
                    "date": session.start_time,
                    "attendance": AttendanceSerializer(attendance, many=True).data
                })

            serializer = ClassSessionSerializer(class_sessions, many=True)

            return Response({
                'data': serializer.data,
                'results': results,
                'attendance': attendance_data,
                'total_class': class_sessions_count,
                'total_students': sum([session.total_attendance for session in class_sessions]),
                'total_percentage': round(avg_att, 2)
            }, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Lecturer not found'}, status=status.HTTP_404_NOT_FOUND)

# View for students and lecturers to see their history activities
class UserActivityHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type == "student":
            attendance = Attendance.objects.filter(student__user=user)
            history = [
                {
                    "class_session": att.class_session.id,
                    "course": att.class_session.course.name,
                    "date": att.class_session.duration_time,
                    "status": "Present" if att.is_present else "Absent",
                }
                for att in attendance
            ]
        elif user.user_type == "lecturer":
            class_sessions = ClassSession.objects.filter(lecturer__user=user)
            history = [
                {
                    "class_session": session.id,
                    "course": session.course.name,
                    "date": session.start_time,
                }
                for session in class_sessions
            ]
        else:
            return Response({"error": "User type not supported"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"history": history}, status=status.HTTP_200_OK)

class GetstudentProfile(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            student=Student.objects.get(user=request.user)
            serilizer=GetStudents(student, many=False)
        except Exception as e:
            return Response({'error':str(e)})
        
        return Response({"data": serilizer.data}, status=status.HTTP_200_OK)
    

# View to return all students of a department course with the number of times they have been present
class CourseAttendanceSummaryView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, pk):
        try:
            course = Course.objects.get(id=pk)
            students = Student.objects.filter(department=course.department)
            attendance_summary = []
            for student in students:
                attendance_present= Attendance.objects.filter(
                    class_session__course=course, student=student, is_present=True
                ).count()
                total_absent= students.count()-attendance_present
                total_present=Attendance.objects.filter(
                    class_session__course=course,  is_present=True
                ).count()
                attendance_summary.append({
                    "student": {
                        "id": student.id,
                        "name": f"{student.user.first_name} {student.user.last_name}",
                        "matricule_number": student.matricule_number,
                    },
                    "attendance_count": attendance_present,
                })
            return Response({"course": course.name + ' ' + course.code, 'department':course.department.name,'total_present':total_present, 'total_absent':total_absent, "attendance_summary": attendance_summary}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "Course or students not found"}, status=status.HTTP_404_NOT_FOUND)




