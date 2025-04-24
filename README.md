Attendee API Documentation

The Attendee API is a Django-based system designed to manage student attendance, class sessions, and related entities like users, schools, departments, courses, and more. This documentation provides a detailed overview of the models, endpoints, and their functionality.
using the link https://attendee-api.onrender.com/Attendee/ as the moter link to all othe links of the site
Data Models

User Model
The User model extends AbstractUser and includes custom fields for distinguishing between students and lecturers.

- Fields:
  - role_choice: Specifies the user role (student or lecturer).
  - user_type: The type of user, determined by role_choice.
  - first_name, last_name: Name fields.
  - email: Email field, required and unique.
  - phone: Phone number, default value is 670000000.

Student Model
Represents an individual student.

- Fields:
  - user: One-to-one relationship with the User model (limited to student type).
  - matricule_number: Unique matricule number for the student.
  - school: ForeignKey to Schools (many-to-one relationship).
  - department: ForeignKey to Department (many-to-one relationship).

Lecturer Model
Represents an individual lecturer.

- Fields:
  - user: One-to-one relationship with the User model (limited to lecturer type).
  - matricule_number: Unique matricule number for the lecturer.
  - school: Many-to-many relationship with Schools.
  - department: Many-to-many relationship with `Departments`.

Course Model
Represents a course offered in a department.

- Fields:
  - name: Name of the course.
  - department: ForeignKey to Department.
  - code: Unique course code.

ClassSession Model
Represents a session for a specific course.

- Fields:
  - course: ForeignKey to Course.
  - lecturer: ForeignKey to Lecturer.
  - start_time, end_time: Session start and end times.
  - qr_code: QR code for attendance marking.


Attendance Model
Tracks attendance for a class session.

- Fields:
  - is_present: Boolean field indicating if a student is present.
  - class_session: ForeignKey to ClassSession.







API Endpoints

Authentication
Attendee uses Jason web tokens for user authentication and also store refreshment tokens to avoid the user from login in each time the token expires

1. Register Student
   - Endpoint:/register/student/
   - Method:POST
   - Description: Registers a new student.
   - Request Body:
     json
     {
       "first_name": "string",
       "last_name": "string",
       "email": "string",
       "password": "string",
       "school": "int",
       "department": "int",
       "matricule_number": "string"

     }
     

2. Register Lecturer
   - Endpoint: /register/lecturer/
   - Method:POST
   - Description: Registers a new lecturer.
   - Request Body:
     json
     {
       "first_name": "string",
       "last_name": "string",
       "email": "string",
       "password": "string",
       
       "matricule_number": "string"
     }
     

3. Login
   - Endpoint:/login/
   - Method:POST
   - Description: Authenticates a user using Jason web tokens.
   - Request Body:
     
     {
       "username": "string",
       "password": "string"
       "token": token stored on local storage

     }
     

4. Logout
   - Endpoint:/logout/
   - Method:POST
   - Description:Logs out the authenticated user.

Class Sessions

1. Get Student Class Sessions
   - Endpoint:/student/class-sessions/<int:pk>/
   - Method:GET
   - Description: Retrieves all class sessions for a specific student.
   - Path Parameters: pk - Student ID.

2. Create Class Session
   - Endpoint:/lecturer/create-class-sessions/
   - Method:POST
   - Description:Allows a lecturer to create a new class session.
   - Request Body:
     json
     {
       "course_id": "int",
       "start_time": "YYYY-MM-DDTHH:MM:SS",
       "end_time": "YYYY-MM-DDTHH:MM:SS"

     }
     

3. Mark Attendance
   - Endpoint: /attendance/<int:pk>/
   - Method :POST
   - Description: Marks attendance for a class session.
   - Path Parameters: pk - Class session ID.
   - Request Body:
     json
     {
       'is_present':[Boolean],
       'student_id':[request.user.id],
       'course_id:pk
     }
     
Data Retrieval

1. Get Schools
   - Endpoint: /schools/
   - Method: GET
   - Description: Retrieves a list of all schools.

2. Get Departments
   - Endpoint:/department/<int:pk>/
   - Method: GET
   - Description: Retrieves details of a specific department.
   - Path Parameters: pk - Department ID.

3. Get Courses
   - Endpoint: /course/<int:pk>/
   - Method:GET
   - Description:Retrieves all courses in a department.
   - Path Parameters:pk- Department ID.

4. Get Students in Department
   - Endpoint:/students/school/<int:pks>/department/<int:pkd>/
   - Method:GET
   - Description: Retrieves all students in a specific school and department.
   - Path Parameters:
     - pks: School ID.
     - pkd: Department ID.

5. Get Attendance
   - Endpoint:/class-sessions/<int:pk>/attendance/
   - Method:GET
   - Description: Retrieves attendance details for a class session.
   - Path Parameters: pk - Class session ID.

6. Update Class Session
   - Endpoint: /lecturer/class-sessions/update/<int:pk>/
   - Method: PUT
   - Description:Updates a class session.
   - Path Parameters:pk- Class session ID.
   - Request Body:
     Json
     {
       "start_time": "YYYY-MM-DDTHH:MM:SS",
       "end_time": "YYYY-MM-DDTHH:MM:SS"
     }
  Data Structure for Each Class
7. get student attendance and total attendance of a course
  - Endpoint: /course/attendance-summary/<int:pk>/
   - Method: GET
   - Description:gets the total count of absentees and presents of s course and return all the students with thier attendance status and count of that course
   - Path Parameters:pk- Class session ID.
   

8 User activity history (students and lecturers)
    -Endpoint : /user/activity-history/'
    - Method: GET
   - Description:gets user history past activities like attendance and class session creating


9 Lecturer access to past class session attendance
    -Endpoint : /lecturer/past-attendance/<int:pk>/
    - Method: GET
   - Description:gets the past class sessions and attendance for a lucturer 
   - Path Parameters:pk- Class session ID.

10.Get user Details
   -Endpoint: /user/

     
  Data Structure for Each Class

● User
  
The User class represents both students and lecturers. It provides essential user details.


Data Variables
{
"id": "integer",
"user_type": "string",
"first_name": "string",
"last_name": "string",
"email": "string",
"phone": "integer"
}

● Student
  
The Student class extends the User class and includes additional student-specific details. 

Data Variables
{
"id": "integer",
"user": {
"id": "integer",
"user_type": "string",
"first_name": "string",
"last_name": "string",
"email": "string",
"phone": "integer"
},
"matricule_number": "string",  // matrucule is in the format UBaXXYYZZZ where XX is a number from 10 to 24, YYY  are letters from A to Z, and ZZZ is a number from 000 to 999

"school": {
"id": "integer",
"name": "string"
},
"department": {
"id": "integer",
"name": "string"
}
}

● Lecturer
  
The Lecturer class extends the User class and includes additional lecturer-specific details.

Data Variables
{
"id": "integer",
"user": {
"id": "integer",
"user_type": "string",
"first_name": "string",
"last_name": "string",
"email": "string",
"phone": "integer"
},
"matricule_number": "string",  //matrucule is in the format UBaLecXXYZZZZ where XX is a number from 10 to 24, Y is a  letters from A to Z, and ZZZZ is a number from 0000 to 9999

"school": {
"id": "integer",
"name": "string"
}
"department": 
{
"id": "integer",
"name": "string"
}
}

● School

The School class represents schools in the system.

Data Variables
{
"id": "integer",
"name": "string"
}

● Department
  
The Department class represents departments within schools.

Data Variables
{
"id": "integer",
"name": "string",
"school": {
"id": "integer",
"name": "string"
}
}

● Course
  
The Course class represents courses offered in departments.

Data Variables
{
"id": "integer",
"name": "string",
"department": {
"id": "integer",
"name": "string"
},
"code": "string"
}

● ClassSession
  
The ClassSession class represents an individual session for a course.

Data Variables
{
"id": "integer",
"course": {
"id": "integer",
"name": "string",
"department": {
"id": "integer",
"name": "string"
},
"code": "string"
},
"lecturer": {
"id": "integer",
"user": {
"id": "integer",
"first_name": "string",
"last_name": "string"
},
"matricule_number": "string"
},
"start_time": "datetime",
"end_time": "datetime",
"qr_code": "string" 
}

● Attendance
  
The Attendance class tracks attendance for a specific class session.

Data Variables
{
"id": "integer",
"is_present": "boolean",
"class_session": {
"id": "integer",
"start_time": "datetime",
"end_time": "datetime",
"course": {
"id": "integer",
"name": "string"
}
},
"student": {
"id": "integer",
"user": {
"id": "integer",
"first_name": "string",
"last_name": "string"
},
"matricule_number": "string"
},
"attendance_time": "datetime"
}

● Summary of Relationships

Here's a quick guide to how the models are connected:
- User Linked to Student or Lecturer.
- Student Linked to School and Department.
- Lecturer Linked to multiple Schools and Departments.
- Course Linked to a Department.
- ClassSession Linked to a Course and a Lecturer.
- Attendance Linked to a ClassSession and a Student.







     

