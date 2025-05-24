from rest_framework import serializers
from base.models import User, Student, Lecturer, Schools, Department, ClassSession, Attendance, Course
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

def student_matricule_validator(value):
    pattern=  r'^UBa(1[0-9]|2[0-4])([A-Z]{2})(\d{3})$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid Matricule format. Please use the format UBaXXYYZZZ where XX is a number between 10-24, YY is are two letters and ZZZ is a number betwenn 001 - 999')

def lecturer_matricule_validator(value):
    pattern=r'^UBaLec(1[0-9]|2[0-4])([A-Z]{1})(\d{4})$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid Matricule format. Please contact admin for a valid matricule number')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields='__all__'
class RegisterStudentSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.IntegerField()
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255, write_only=True)
    school_name = serializers.CharField(max_length=255)
    department_name = serializers.CharField(max_length=255)
    matricule_number = serializers.CharField(max_length=255, validators=[student_matricule_validator])
    device_id = serializers.CharField(max_length=255)

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, data):
        try:
            school = Schools.objects.get(name=data['school_name'])
        except Schools.DoesNotExist:
            raise serializers.ValidationError({'school_name': 'School not found'})

        try:
            department = Department.objects.get(name=data['department_name'])
        except Department.DoesNotExist:
            raise serializers.ValidationError({'department_name': 'Department not found'})

        if department.school != school:
            raise serializers.ValidationError({'department_name': 'Department does not belong to selected school'})

        return data
class RegisterLecturerSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.IntegerField()
    password = serializers.CharField(max_length=255, write_only=True)
    matricule_number = serializers.CharField(max_length=255, validators=[lecturer_matricule_validator])
    device_id = serializers.CharField(max_length=255)

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value


class ClassSessionSerializer(serializers.Serializer):
    course=serializers.CharField()
    start_time=serializers.DateTimeField()
    end_time=serializers.DateTimeField()
    hall=serializers.CharField()
    latitude=serializers.FloatField()
    longitude=serializers.FloatField()
    range_radius=serializers.FloatField()
   
    def validate(self, data):
        try:
            
            course=Course.objects.get(name=data['course'])
            if course is None:
                serializers.ValidationError({'error':'course not found'})
        except Course.DoesNotExist:
            raise serializers.ValidationError({'error':'course not found'})
        
        return data
        
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['first_name','last_name', 'phone', 'email']

class GetStudents(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model= Student
        fields='__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    student=GetStudents()
    class Meta:
        model = Attendance
        fields = '__all__'

class ClassSessionAttendanceSerializer(serializers.Serializer):
    
    course=serializers.CharField()
    start_time=serializers.DateTimeField()
    end_time=serializers.DateTimeField()
    hall=serializers.CharField()
    latitude=serializers.FloatField()
    longitude=serializers.FloatField()
    lecturer=serializers.CharField()
    id=serializers.IntegerField()
    range_radius=serializers.FloatField()
        


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    device_id = serializers.CharField(max_length=255)

