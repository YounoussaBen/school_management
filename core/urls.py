from django.urls import path
from . import views

urlpatterns = [
    path('students/login/', views.student_login, name='student_login'),
    path('students/logout/', views.student_logout, name='student_logout'),
    path('students/', views.student_home, name='student_home'),
    path('students/courses/', views.student_courses, name='student_courses'),
    path('students/attendance/', views.student_attendance, name='student_attendance'),
    path('students/report/<int:course_id>/', views.download_report, name='download_report'),


    path('teachers/login', views.teacher_login, name='teacher_login'),
]
