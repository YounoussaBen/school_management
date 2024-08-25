from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),


    path('students/login/', views.student_login, name='student_login'),
    path('students/', views.student_home, name='student_home'),
    path('students/course/', views.student_course, name='student_course'),
    path('students/attendance/', views.student_attendance, name='student_attendance'),
    path('students/report/<int:course_id>/', views.download_report, name='download_report'),


    path('teachers/login', views.teacher_login, name='teacher_login'),
    path('teachers/', views.teacher_home, name='teacher_home'),
    path('teachers/attendance/', views.teacher_attendance, name='teacher_attendance'),
    path('teachers/subjects/', views.teacher_subjects, name='teacher_subjects'),
    path('api/upload-grades/', views.upload_grades, name='upload-grades'),

]
