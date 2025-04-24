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
)
from base.models import User, Student, Lecturer, Schools, Department, Course, ClassSession, Attendance
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime




# Helper function for generating JWT tokens
def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


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
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            tokens = generate_tokens(user)
            login(request, user)
            return Response(
                {"message": "Logged in successfully", "tokens": tokens},
                status=status.HTTP_200_OK,
            )
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# Protected route
class ProtectedRoute(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Welcome, {request.user.username}"}, status=status.HTTP_200_OK)


# Get all class sessions for a student
class StudentClassSessionView(APIView):
    
    permission_classes=[IsAuthenticated]
    def get(self, request, pk):
        try:
            student = Student.objects.get(id=pk)
            class_sessions = ClassSession.objects.filter(course__department=student.department)
            serializer = ClassSessionSerializer(class_sessions, many=True)
            return Response({'student':student.user.first_name + ' ' + student.user.last_name,'school':student.school.name, 'department':student.department.name ,'sessions':[ {"data": serializer.data}]}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)


# Get all students in a department of a school
class GetDepartmentStudents(APIView):
    permission_classes = [IsAuthenticated, ]
    

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
    permission_classes=[IsAuthenticated]

    def post(self, request):
        serializer = ClassSessionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                class_session = ClassSession.objects.create(
                    course=Course.objects.get(name=serializer.validated_data["course"]),
                    end_time=serializer.validated_data["end_time"],
                    latitude=serializer.validated_data["latitude"],
                    longitude=serializer.validated_data["longitude"],
                    lecturer=Lecturer.objects.get(user=request.user.id),
                    
                )
                return Response(
                    {"message": "Class session created successfully", "data": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
            except ObjectDoesNotExist:
                return Response({"error":"Lecturer or course not found" }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update class sessions
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
        
class GetClassSession(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, pk):
        try:
           
            class_session=ClassSession.objects.get(id=pk)
            serializer=ClassSessionSerializer(class_session, many=True)
          
                
            context={
                'course':class_session.course.name,
                'id':class_session.id,
                'start time':class_session.start_time,
                'end time':class_session.end_time,
                'lecturer':class_session.lecturer.user.first_name + ' ' + class_session.lecturer.user.last_name
            }
            return Response({'data':[context]}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'class session does not found'}, status=status.HTTP_404_NOT_FOUND)


#Mark attendance of an ongoing class class session course
class AttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            class_session = ClassSession.objects.get(id=pk)
            student = Student.objects.get(user=request.user.id)
            attendance = Attendance.objects.create(class_session=class_session, student=student)
            attendance.save()
            return Response({'message': 'Attendance marked successfully'})
        except ObjectDoesNotExist:
            return Response({'error': 'Class session or student not found'}, status=status.HTTP_404_NOT_FOUND)
        

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
        return Response([{'id': school.id, 'name':school.name} for school in schools])

#Get all available departments
class DepartmentView(APIView):
    def get(self, request, pk):
        try:
            school=Schools.objects.get(id=pk)
            departments=Department.objects.filter(school=school)
            return Response({'School':school.name, 'Departments':[{'id':department.id, 'name':department.name} for department in departments]})
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
        if not request.user.is_authenticated:
            return Response({'error': 'User is not authenticated'}, status=401)
        
        try:
            on_user = request.user.id
            user = User.objects.get(id=on_user)
            
            return Response({
                'user': [{
                    'username': user.username,
                    'first name': user.first_name,
                    'last name': user.last_name,
                    'user type': user.user_type,
                }]
            })

        except ObjectDoesNotExist:
            return Response({'error': 'User does not exist'}, status=404)
        
#logout users
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token=request.data['refresh']
            token=RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({'message':'logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error':e}, status=status.HTTP_400_BAD_REQUEST)

# Lecturer access to past class session attendance
class LecturerPastAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            lecturer = Lecturer.objects.get(user=request.user)
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
                    "date": att.class_session.start_time,
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
            return Response({"course": course.name, 'department':course.department.name,'total_present':total_present, 'total_absent':total_absent, "attendance_summary": attendance_summary}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "Course or students not found"}, status=status.HTTP_404_NOT_FOUND)




