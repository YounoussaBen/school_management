from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Subject, Course, Attendance, Grade
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime
from calendar import monthrange


# Student Login View
def student_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.role == 'Student':
            login(request, user)
            return redirect('student_profile')
        else:
            return render(request, 'students/login.html', {'error': 'Invalid credentials'})
    return render(request, 'students/login.html')

# Student Profile View
@login_required
def student_profile(request):
    if request.user.role != 'Student':
        return redirect('student_login')
    return render(request, 'students/profile.html', {'student': request.user})

@login_required
def student_courses(request):
    if request.user.role != 'Student':
        return redirect('student_login')

    # Get the course the student is enrolled in
    course = Course.objects.filter(students=request.user).first()

    # Get the subjects under the student's course
    subjects = Subject.objects.filter(course=course)

    # Get the grades for the subjects the student is enrolled in
    grades = Grade.objects.filter(student=request.user, subject__in=subjects)

    return render(request, 'students/course.html', {
        'course': course,
        'subjects': subjects,
        'grades': grades
    })


# Student Attendance View
@login_required
def student_attendance(request):
    # Get the current month and year
    today = datetime.now()
    year = today.year
    month = today.month

    # Get the number of days in the current month
    _, num_days = monthrange(year, month)

    # Get all subjects for the student
    subjects = Subject.objects.filter(course__students=request.user)

    # Prepare the calendar data
    calendar_data = []
    for subject in subjects:
        subject_attendance = []
        for day in range(1, num_days + 1):
            date = datetime(year, month, day).date()
            try:
                attendance = Attendance.objects.get(student=request.user, subject=subject, date=date)
                status = attendance.status
            except Attendance.DoesNotExist:
                status = '-'
            subject_attendance.append(status)
        calendar_data.append({
            'subject': subject,
            'attendance': subject_attendance
        })

    context = {
        'calendar_data': calendar_data,
        'days': range(1, num_days + 1),
        'month': today.strftime('%B'),
        'year': year,
    }

    return render(request, 'students/attendance.html', context)

# Download PDF Report View
@login_required
def download_report(request, course_id):
    if request.user.role != 'Student':
        return redirect('student_login')
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
