from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from api.views import StudentRegisterView, LecturerRegisterView, LoginView, LogoutView, StudentClassSessionView, LecturerClassSessionView,AttendanceView, SchoolView, DepartmentView, CourseView, GetDepartmentStudents, GetStudentsAttendance, GetClassSession, GetClassSession, LecturerClassSessionUpdateView, GetUserData, ProtectedRoute, LecturerViewAllClassSessionView, GetstudentProfile, SessionProximityCheckView
from django.urls import path
from api.views import (
    LecturerPastAttendanceView,
    UserActivityHistoryView,
    CourseAttendanceSummaryView,
)
from .views import (index, createstudent, getdepartments, createLecturer, lecturerDasboard, studentDashboard, user_login, user_logout)
urlpatterns = [
    #views urls
    path('home/', index, name='index'),
    path('create-account/student',  createstudent,  name="create-student"),
    path('create-account/lecturer',  createLecturer,  name="create-lecturer"),
    path("get-department/", getdepartments, name="getdepartments"),
    path("dashboard/lecturer/", lecturerDasboard, name="lecturer-dashboard"),
    path("dashboard/student/", studentDashboard, name="student-dashboard"),
    path("signin/", user_login, name="login"),
    path("signout/", user_logout, name="logout"),
    
    #api urls
    path('register/student/', StudentRegisterView.as_view()), #register students
    path('register/lecturer/', LecturerRegisterView.as_view()),#register lecturers
    path('login/', LoginView.as_view()),#login
    path("token/", TokenObtainPairView.as_view(), name=""),
    path('logout/', LogoutView.as_view()),#logout
    path('student/class-sessions/', StudentClassSessionView.as_view()),#student to get a class sseion
    path('user/', GetUserData.as_view()),
    path('lecturer/create-class-sessions/', LecturerClassSessionView.as_view()),#lectruree to create a class sesiosn
    path('attendance/<int:pk>/', AttendanceView.as_view()),# students to mark attendance
    path('school-department-course/', SchoolView.as_view()),# get schhols
    path('department/<str:school_name>/', DepartmentView.as_view()),#get departments
    path('course/<int:pk>/', CourseView.as_view()),#get all courses in a department
    path('students/school/<int:pks>/department/<int:pkd>/', GetDepartmentStudents.as_view()),#get all students in a departmet from a school
    path('class-sessions/<int:pk>/attendance/', GetStudentsAttendance.as_view()),#get all students attendance from a class session
    path('course/<int:pk>/class-sessions/', GetClassSession.as_view()),#get all class sesions in a course
    path('course/class-session/<int:pk>/', GetClassSession.as_view()),# get a class session
    path('lecturer/class-sessions/update/<int:pk>', LecturerClassSessionUpdateView.as_view()),#update a class session
    path('protected/', ProtectedRoute.as_view()),
    # Lecturer access to past class session attendance
    path('lecturer/past-attendance/<int:pk>/', LecturerPastAttendanceView.as_view(), name='lecturer-past-attendance'),

    # User activity history (students and lecturers)
    path('user/activity-history/', UserActivityHistoryView.as_view(), name='user-activity-history'),

    # Course attendance summary
    path('course/attendance-summary/<int:pk>/', CourseAttendanceSummaryView.as_view(), name='course-attendance-summary'),
    path("lecturer/class-sessions/", LecturerViewAllClassSessionView.as_view(), name=""),
    path("profile", GetstudentProfile.as_view(), name=""),
    path('student/access-session/', SessionProximityCheckView.as_view(), name='session-access-check'),
]



