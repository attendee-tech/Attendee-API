from rest_framework import serializers
from base.models import User, Student, Lecturer, Schools, Department, ClassSession, Attendance
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

class RegisterStudentSerializer(serializers.Serializer):
    first_name=serializers.CharField(max_length=100)
    last_name=serializers.CharField(max_length=100)
    phone=serializers.IntegerField()
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255, write_only=True)
    school_name = serializers.CharField(max_length=255)
    department_name = serializers.CharField(max_length=255)
    matricule_number = serializers.CharField(max_length=255, validators=[student_matricule_validator])
    

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, data):
        try:
            school=Schools.objects.get(name=data['school_name'])
            department=Department.objects.get(name=data['department_name'])
            if department.school != school:
                raise serializers.ValidationError({'error':'Department does not belong to selected school'})
        except Schools.DoesNotExist:
                raise serializers.ValidationError({'error':'School found'})
        except Department.DoesNotExist:
                raise serializers.ValidationError({'error':'Department ot found'})
        
        return data

class RegisterLecturerSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255, write_only=True)
    school_name= serializers.IntegerField()
    department_name= serializers.IntegerField()
    matricule_number = serializers.CharField(max_length=255, validators=[student_matricule_validator])

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, data):
        try:
            school=Schools.objects.get(name=data['school_name'])
            department=Department.objects.get(name=data['department_name'])
            if department.school != school:
                raise serializers.ValidationError({'error':'Department does not belong to selected school'})
        except Schools.DoesNotExist:
                raise serializers.ValidationError({'error':'School found'})
        except Department.DoesNotExist:
                raise serializers.ValidationError({'error':'Department ot found'})
        
        return data

class ClassSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
        
class GetStudents(serializers.ModelSerializer):
    class Meta:
        model= Student
        fields='__all__'

