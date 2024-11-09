from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator


# Custom user manager
class CustomUserManager(BaseUserManager):
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
        extra_fields.setdefault('role', 'superadmin')

        return self.create_user(email, password, **extra_fields)


# Custom user model
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('superadmin', 'Superadmin'),
    ]
    
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='student')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['email']


# Teacher model
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)


    def __str__(self):
        return f"{self.user.name} ({self.department})"


# Student model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grade_level = models.CharField(max_length=50)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)


    def __str__(self):
        return f"{self.user.name} - Grade: {self.grade_level}"


# Homework model
class Homework(models.Model):
    SUBJECT_CHOICES = [
        ('math', 'Math'),
        ('science', 'Science'),
        ('history', 'History'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='homeworks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.CharField(choices=SUBJECT_CHOICES, max_length=50)
    due_date = models.DateField()
    posted_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.teacher.user.name}"

    class Meta:
        ordering = ['-posted_date']


# Submission model
class Submission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    submission_file = models.FileField(upload_to='homework_submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.name} - {self.homework.title}"
