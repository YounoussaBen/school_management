from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.student_login, name='student_login'),
    path('profile/', views.student_profile, name='student_profile'),
    path('courses/', views.student_courses, name='student_courses'),
    path('attendance/', views.student_attendance, name='student_attendance'),
    path('report/<int:course_id>/', views.download_report, name='download_report'),
]
