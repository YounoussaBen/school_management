from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.student_login, name='student_login'),
    path('logout/', views.student_logout, name='student_logout'),
    path('', views.student_home, name='student_home'),
    path('courses/', views.student_courses, name='student_courses'),
    path('attendance/', views.student_attendance, name='student_attendance'),
    path('report/<int:course_id>/', views.download_report, name='download_report'),
]
