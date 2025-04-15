from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serilizers import RegisterStudentSerializer, RegisterLecturerSerializer, ClassSessionSerializer, AttendanceSerializer,GetStudents
from base.models import User, Student, Lecturer, Schools, Department, Course, ClassSession, Attendance
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create A student
class StudentRegisterView(APIView):
    def post(self, request):
        try:
            serializer = RegisterStudentSerializer(data=request.data)
            
            if serializer.is_valid():
                
                user = User.objects.create_user(
                    username=serializer.validated_data['username'],
                    first_name=serializer.validated_data['first_name'],
                    last_name=serializer.validated_data['last_name'],
                    phone=serializer.validated_data['phone'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password'],
                    user_type='student'
                )
                student = Student.objects.create(
                    user=user,
                    school=Schools.objects.get(name=serializer.validated_data['school_name']),
                    department=Department.objects.get(name=serializer.validated_data['department_name']),
                    matricule_number=serializer.validated_data['matricule_number'],
                )
                refresh = RefreshToken.for_user(user)
                login(request, user)
                
                return Response({   'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

#Create a lecturer
class LecturerRegisterView(APIView):
    def post(self, request):
        try:
            serializer = RegisterLecturerSerializer(data=request.data)
            if serializer.is_valid():
                user = User.objects.create_user(
                    username=serializer.validated_data['username'],
                    first_name=serializer.validated_data['first_name'],
                    last_name=serializer.validated_data['last_name'],
                    phone=serializer.validated_data['phone'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password'],
                    user_type='lecturer'
                )
                lecturer = Lecturer.objects.create(
                    user=user,
                    school=Schools.objects.get(name=serializer.validated_data['school_name']),
                    department=Department.objects.get(name=serializer.validated_data['department_name']),
                    matricule_number=serializer.validated_data['matricule_number'],
                )
                refresh = RefreshToken.for_user(user)
                login(request, user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#User authentication
class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        try:
            username = request.data['username']
            password = request.data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                login(request, user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'success':'Logged in successfully'
                })
                
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Get and return all available class sessions for students
class StudentClassSessionView(APIView):
    def get(self, request, pk):
        try:
            student = Student.objects.get(id=pk)
            class_sessions = ClassSession.objects.filter(course__department=student.department)
            serializer = ClassSessionSerializer(class_sessions, many=True)
            return Response({'data':serializer.data})
            
     
        except ObjectDoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

#Get and return all available student in a department of a school 
class GetDepartmentStudents(APIView):
    def get(self, request, pks, pkd):
        try:
            
            school=Schools.objects.get(id=pks)
            department=Department.objects.get(id=pkd, school=school)
            students=Student.objects.filter(school=school, department=department)
            serializer=GetStudents(students, many=True)
            
        
            return Response({'school':school.name, 'department':department.name, 'students':[{'data':serializer.data}]})
        except ObjectDoesNotExist:
            return Response({'error': 'School or Department not found'}, status=status.HTTP_404_NOT_FOUND)

#create class sessions
class LecturerClassSessionView(APIView):
    

    def post(self, request):
        try:
            lecturer = Lecturer.objects.get(user=request.user)
            serializer = ClassSessionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(lecturer=lecturer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'error': 'Lecturer not found'}, status=status.HTTP_404_NOT_FOUND)
        
class LecturerClassSessionUpdateView(APIView):
    

    def put(self, request, pk):
        try:
            class_session=ClassSession.objects.get(id=pk)
            
            serializer = ClassSessionSerializer(class_session, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'data':serializer.data}, status=status.HTTP_201_CREATED)
            return Response({ 'errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'error': 'Lecturer not found'}, status=status.HTTP_404_NOT_FOUND)
        
class GetClassSessions(APIView):
    
    def get(self, request, pk):
        try:
            course=Course.objects.get(id=pk)
            class_sessions=ClassSession.objects.filter(course=course)
            serializer=ClassSessionSerializer(class_sessions, many=True)
            return Response({'data':serializer.data}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'course or class session does not found'}, status=status.HTTP_404_NOT_FOUND)
        
class GetClassSession(APIView):
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
            student = Student.objects.get(user=request.user)
            attendance = Attendance.objects.create(class_session=class_session, student=student)
            attendance.save()
            return Response({'message': 'Attendance marked successfully'})
        except ObjectDoesNotExist:
            return Response({'error': 'Class session or student not found'}, status=status.HTTP_404_NOT_FOUND)
        

class GetStudentsAttendance(APIView):
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
        
        
        
        
        