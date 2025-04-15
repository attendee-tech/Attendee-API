from django.shortcuts import render
from .models import Schools, Lecturer, Student, Attendance, Course, User, Department
from django.http import HttpResponse, JsonResponse

# Create your views here.
def index(request):
    schools=Schools.objects.all()

def deparments(request, pk):
    schools=Schools.objects.get(id=pk)
    deparments=schools.department_set.all()
    print(deparments)
    