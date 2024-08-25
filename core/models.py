from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('Student', 'Student'),
        ('Teacher', 'Teacher'),
        ('Staff', 'Staff'),
    )
    
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    dob = models.DateField(null=True, blank=True)  # Optional field
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    conduct = models.TextField(null=True, blank=True)
    interest = models.TextField(null=True, blank=True)
    attitude = models.TextField(null=True, blank=True)
    class_teacher_remark = models.TextField(null=True, blank=True)
    head_teacher_remark = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} Profile"


class Course(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Teacher'})
    students = models.ManyToManyField(User, related_name='courses', limit_choices_to={'role': 'Student'})

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Teacher'})
    credits = models.PositiveIntegerField(default=3)

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    def __str__(self):
        return f"Attendance for {self.student.first_name} {self.student.last_name} on {self.date}"


class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_score = models.DecimalField(max_digits=5, decimal_places=2)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    grade = models.CharField(max_length=2)
    remarks = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total_score = round((self.class_score + self.exam_score)/2, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Grade for {self.student.first_name} {self.student.last_name} in {self.subject.name}"
