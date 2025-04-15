from django.contrib import admin

from .models import User, Schools, Student, Lecturer, Department, Attendance, Course, ClassSession

 
# Register your models here.

admin.site.register(User)
admin.site.register(Schools)
admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Attendance)
admin.site.register(ClassSession)