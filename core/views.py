from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Subject, Course, Attendance, Grade, User
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime, timedelta
from django.utils import timezone


def home(request):
    return render(request, 'home.html')

# Student Login View
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

# Student Logout View
@login_required(login_url='home')
def user_logout(request):
    logout(request)
    return redirect('home')

# Student Home View
@login_required(login_url='home')
def student_home(request):
    if request.user.role != 'Student':
        return redirect('home')

    course = Course.objects.filter(students=request.user).first()

    grades = Grade.objects.filter(student=request.user)
    if grades.exists():
        total_score = sum(grade.total_score for grade in grades)
        overall_gpa = round(total_score / grades.count(), 2)
    else:
        overall_gpa = 'N/A'

    total_classes = Attendance.objects.filter(student=request.user).count()
    attended_classes = Attendance.objects.filter(student=request.user, status='Present').count()
    unattended_classes = Attendance.objects.filter(student=request.user, status='Absent').count()

    attendance_rate = round((attended_classes / total_classes) * 100, 2) if total_classes > 0 else 0
    absence_rate = round((unattended_classes / total_classes) * 100, 2) if total_classes > 0 else 0

    recent_grades = Grade.objects.filter(student=request.user).order_by('-id')[:5]
    recent_attendance = Attendance.objects.filter(student=request.user).order_by('-date')[:5]

    recent_activities = sorted(
        list(recent_grades) + list(recent_attendance),
        key=lambda x: getattr(x, 'date', getattr(x, 'subject', None)),
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

    course = Course.objects.get(id=course_id)
    grades = Grade.objects.filter(student=request.user, subject__course=course)
    attendance = Attendance.objects.filter(student=request.user)
    template_path = 'students/report_template.html'
    context = {
        'student': request.user,
        'course': course,
        'grades': grades,
        'attendance': attendance
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{course.name}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


# Teacher Login View
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

    # Get total number of unique students across all subjects taught by the teacher
    total_students = User.objects.filter(
        role='Student',
        courses__subjects__teacher=request.user
    ).distinct().count()

    # Get today's date
    today = datetime.now().date()

    # Fetch Recent Activities (e.g., new grades, attendance, etc.)
    recent_grades = Grade.objects.filter(subject__teacher=request.user).order_by('-id')[:5]
    recent_attendance = Attendance.objects.filter(subject__teacher=request.user, date=today).order_by('-id')[:5]

    recent_activities = sorted(
        list(recent_grades) + list(recent_attendance),
        key=lambda x: getattr(x, 'date', getattr(x, 'created_at', None)),
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
                student = User.objects.get(id=student_id)
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
    # Logic for viewing subject details
    return render(request, 'teachers/subject.html')

@login_required
def teacher_upload_grades(request):
    # Logic for viewing and uploading grades via Excel for each subject
    return render(request, 'teachers/upload_grades.html')

