from django.contrib import admin
from .models import User, StudentProfile, Course, Subject, Attendance, Grade

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'conduct', 'interest', 'attitude')

@admin.register(Course)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'course')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'class_score', 'exam_score', 'total_score', 'grade')
