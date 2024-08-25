from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Subject, Course, Attendance, Grade, User, StudentProfile
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from .utils import get_grade_letter, get_gpa
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F
from weasyprint import HTML


def home(request):
    return render(request, 'home.html')

# Logout View
@login_required(login_url='home')
def user_logout(request):
    logout(request)
    return redirect('home')


# Student  View
def student_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.role == 'Student':
            login(request, user)
            return redirect('student_home')
        else:
            return render(request, 'students/login.html', {'error': 'Invalid credentials'})
    return render(request, 'students/login.html')

@login_required(login_url='home')
def student_home(request):
    if request.user.role != 'Student':
        return redirect('home')

    course = Course.objects.filter(students=request.user).first()

    grades = Grade.objects.filter(student=request.user)
    if grades.exists():
        total_weighted_gpa = sum(get_gpa(grade.total_score) * grade.subject.credits for grade in grades)
        total_credits = sum(grade.subject.credits for grade in grades)
        overall_gpa = round(total_weighted_gpa / total_credits, 2)
    else:
        overall_gpa = 'N/A'


    total_classes = Attendance.objects.filter(student=request.user).count()
    attended_classes = Attendance.objects.filter(student=request.user, status='Present').count()
    unattended_classes = Attendance.objects.filter(student=request.user, status='Absent').count()

    attendance_rate = round((attended_classes / total_classes) * 100, 2) if total_classes > 0 else 0
    absence_rate = round((unattended_classes / total_classes) * 100, 2) if total_classes > 0 else 0

    today = datetime.now().date()

        # Fetch Recent Activities (e.g., new grades, attendance, etc.)
    recent_grades = Grade.objects.filter(student=request.user).order_by('-id')[:5]
    recent_attendance = Attendance.objects.filter(student=request.user).order_by('-date')[:5]

    # Combine recent grades and attendance and sort them by date
    recent_activities = sorted(
        list(recent_grades) + list(recent_attendance),
        key=lambda x: getattr(x, 'date', getattr(x, 'created_at', today)),  # Use today as a default date
        reverse=True
    )[:5]

    context = {
        'student': request.user,
        'course_name': course.name if course else 'Not enrolled in any course',
        'overall_gpa': overall_gpa,
        'attendance_rate': attendance_rate,
        'absence_rate': absence_rate,
        'recent_activities': recent_activities,
    }

    return render(request, 'students/home.html', context)

@login_required(login_url='home')
def student_course(request):
    if request.user.role != 'Student':
        return redirect('home')

    course = Course.objects.filter(students=request.user).first()
    subjects = Subject.objects.filter(course=course)
    grades = Grade.objects.filter(student=request.user, subject__in=subjects)

    return render(request, 'students/course.html', {
        'student': request.user,
        'course': course,
        'subjects': subjects,
        'grades': grades
    })

@login_required(login_url='home')
def student_attendance(request):
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    subjects = Subject.objects.filter(course__students=request.user)
    calendar_data = []

    for subject in subjects:
        subject_attendance = {}
        for day in range(7):
            date = (week_start + timedelta(days=day)).date()
            try:
                attendance = Attendance.objects.get(student=request.user, subject=subject, date=date)
                status = attendance.status
            except Attendance.DoesNotExist:
                status = '-'
            subject_attendance[date] = status
        calendar_data.append({
            'subject': subject,
            'attendance': subject_attendance
        })

    context = {
        'student': request.user,
        'calendar_data': calendar_data,
        'month': today.strftime('%B'),
        'year': today.year,
        'week_start': week_start,
        'week_end': week_end,
    }

    return render(request, 'students/attendance.html', context)

@login_required(login_url='home')
def download_report(request, course_id):
    if not request.user.is_authenticated:
        return redirect('home')

    # Get course and related grades
    course = get_object_or_404(Course, id=course_id)
    grades = Grade.objects.filter(student=request.user, subject__course=course)
    attendance = Attendance.objects.filter(student=request.user)
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    student_id = student_profile.student_id

    # Calculate overall GPA based on credits
    if grades.exists():
        total_weighted_gpa = sum(get_gpa(grade.total_score) * grade.subject.credits for grade in grades)
        total_credits = sum(grade.subject.credits for grade in grades)
        overall_gpa = round(total_weighted_gpa / total_credits, 2)
    else:
        overall_gpa = 'N/A'

    # Calculate overall position
    all_students_gpa = Grade.objects.filter(subject__course=course).values('student').annotate(
        gpa=Sum(F('total_score') * F('subject__credits')) / Sum('subject__credits')
    ).order_by('-gpa')
    student_gpa = all_students_gpa.filter(student=request.user.id).first().get('gpa')
    overall_position = all_students_gpa.filter(gpa__gt=student_gpa).count() + 1

    # Calculate subject positions
    subject_positions = {}
    for grade in grades:
        subject_scores = Grade.objects.filter(subject=grade.subject).values('student').annotate(
            total_score=Sum(F('total_score'))
        ).order_by('-total_score')
        student_score = subject_scores.filter(student=request.user.id).first().get('total_score')
        subject_position = subject_scores.filter(total_score__gt=student_score).count() + 1
        subject_positions[grade.subject.id] = subject_position

    # Attendance details
    days_present = attendance.filter(status='Present').count()
    total_days = attendance.count()
    
    # Prepare teacher's remarks
    conduct = student_profile.conduct
    interest = student_profile.interest
    attitude = student_profile.attitude
    class_teacher_remark = student_profile.class_teacher_remark
    head_teacher_remark = student_profile.head_teacher_remark if student_profile.head_teacher_remark else ''
    today = datetime.now().date()

    # Prepare context for the PDF template
    context = {
        'school_logo_url': 'https://play-lh.googleusercontent.com/y3x_qIXz5sKBn4hEG0HzmJc-neevDBMzP4WvepMZzPlBBMzgRYxKP_bwEytYM_A5UKCk',
        'student': request.user,
        'course': course,
        'grades': [
            {
                'subject': grade.subject,
                'class_score': grade.class_score,
                'exam_score': grade.exam_score,
                'total_score': grade.total_score,
                'grade': get_grade_letter(grade.total_score),
                'subject_position': subject_positions.get(grade.subject.id, 'N/A'),
                'remarks': grade.remarks
            }
            for grade in grades
        ],
        'days_present': days_present,
        'total_days': total_days,
        'conduct': conduct,
        'interest': interest,
        'attitude': attitude,
        'class_teacher_remark': class_teacher_remark,
        'head_teacher_remark': head_teacher_remark,
        'today': today,
        'overall_gpa': overall_gpa,
        'overall_position': overall_position,
        'student_id': student_id
    }
    
    template_path = 'students/report_template.html'
    template = get_template(template_path)
    html = template.render(context)
    
    # Generate PDF using WeasyPrint
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{course.name}.pdf"'
    HTML(string=html).write_pdf(response)
    
    return response



# Teacher View
def teacher_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.role == 'Teacher':
            login(request, user)
            return redirect('teacher_home')
        else:
            return render(request, 'teachers/login.html', {'error': 'Invalid credentials'})
    return render(request, 'teachers/login.html')

@login_required
def teacher_home(request):
    if request.user.role != 'Teacher':
        return redirect('home')  # Redirect to home if not a teacher

    # Get the subjects the teacher is teaching
    subjects = Subject.objects.filter(teacher=request.user)

    # Get the total number of unique students across all subjects taught by the teacher
    total_students = User.objects.filter(
        role='Student',
        courses__subjects__teacher=request.user
    ).distinct().count()

    # Get today's date
    today = datetime.now().date()

    # Fetch Recent Activities (e.g., new grades, attendance, etc.)
    recent_grades = Grade.objects.filter(subject__teacher=request.user).order_by('-id')[:5]
    recent_attendance = Attendance.objects.filter(subject__teacher=request.user, date=today).order_by('-id')[:5]

    # Combine recent grades and attendance and sort them by date
    recent_activities = sorted(
        list(recent_grades) + list(recent_attendance),
        key=lambda x: getattr(x, 'date', getattr(x, 'created_at', today)),  # Use today as a default date
        reverse=True
    )[:5]

    context = {
        'teacher': request.user,
        'subjects': subjects,
        'total_students': total_students,
        'recent_activities': recent_activities,
    }

    return render(request, 'teachers/home.html', context)

@login_required
def teacher_attendance(request):
    if request.user.role != 'Teacher':
        return redirect('home')

    today = timezone.now().date()
    teacher = request.user
    subjects = Subject.objects.filter(teacher=teacher)

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('attendance_'):
                _, subject_id, student_id = key.split('_')
                subject = Subject.objects.get(id=subject_id)
                student = User.objects.get(id=student_id, role='Student')
                status = value

                Attendance.objects.update_or_create(
                    date=today,
                    subject=subject,
                    student=student,
                    defaults={'status': status}
                )
        
        return redirect('teacher_attendance')

    attendance_data = {}
    for subject in subjects:
        students = User.objects.filter(courses__subjects=subject, role='Student').distinct()
        attendance_data[subject] = []
        for student in students:
            try:
                attendance = Attendance.objects.get(date=today, subject=subject, student=student)
                status = attendance.status
            except Attendance.DoesNotExist:
                status = None
            attendance_data[subject].append({'student': student, 'status': status})

    context = {
        'teacher': teacher,
        'attendance_data': attendance_data,
        'today': today,
    }

    return render(request, 'teachers/attendance.html', context)

@login_required
def teacher_subjects(request):
    if request.user.role != 'Teacher':
        return redirect('home')

    teacher = request.user
    subjects = Subject.objects.filter(teacher=teacher)

    grades_data = {}
    for subject in subjects:
        students = User.objects.filter(courses__subjects=subject, role='Student').distinct()
        grades_data[subject] = []
        for student in students:
            try:
                grade = Grade.objects.get(subject=subject, student=student)
                student_profile = StudentProfile.objects.get(user=student)
                grade_info = {
                    'class_score': grade.class_score,
                    'exam_score': grade.exam_score,
                    'total_score': grade.total_score,
                    'grade': grade.grade,
                    'conduct': student_profile.conduct,
                    'interest': student_profile.interest,
                    'attitude': student_profile.attitude,
                    'class_teacher_remark': student_profile.class_teacher_remark,
                    'head_teacher_remark': student_profile.head_teacher_remark,
                }
            except (Grade.DoesNotExist, StudentProfile.DoesNotExist):
                grade_info = {
                    'class_score': 'N/A',
                    'exam_score': 'N/A',
                    'total_score': 'N/A',
                    'grade': 'N/A',
                    'conduct': '',
                    'interest': '',
                    'attitude': '',
                    'class_teacher_remark': '',
                    'head_teacher_remark': '',
                }
            grades_data[subject].append({'student': student, 'grade_info': grade_info})

    context = {
        'teacher': teacher,
        'grades_data': grades_data,
        'is_head_teacher': any(subject.course.teacher == teacher for subject in subjects),
    }

    return render(request, 'teachers/subjects.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_grades(request):
    if request.user.role != 'Teacher':
        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    if 'grade_file' not in request.FILES:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

    excel_file = request.FILES['grade_file']
    subject_id = request.data.get('subject_id')

    if not subject_id:
        return Response({"error": "Subject ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

    subject = get_object_or_404(Subject, id=subject_id, teacher=request.user)

    try:
        df = pd.read_excel(excel_file)
        for _, row in df.iterrows():
            student_id = row.get('student_id')
            class_score = row.get('class_score')
            exam_score = row.get('exam_score')
            remarks = row.get('remarks')

            if not all([student_id, class_score, exam_score, remarks]):
                continue  # Skip incomplete rows

            student_profile = get_object_or_404(StudentProfile, student_id=student_id)
            student = student_profile.user
            total_score = (class_score + exam_score) / 2
            grade_letter = get_grade_letter(total_score)

            Grade.objects.update_or_create(
                student=student,
                subject=subject,
                defaults={
                    'class_score': class_score,
                    'exam_score': exam_score,
                    'total_score': total_score,
                    'grade': grade_letter,
                    'remarks': remarks
                }
            )

        return Response({"detail": "Grades uploaded successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

