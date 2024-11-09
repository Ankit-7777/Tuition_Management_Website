from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, TeacherProfileForm, StudentProfileForm, HomeworkForm, SubmissionForm
from .models import User, Teacher, Student, Homework, Submission
from django.views.generic import DetailView, ListView

### Authentication Views ###

def signup_view(request):
    """User Signup and Role-Based Redirect"""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(f"{user.role}_profile_update")
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    """User Login with Role-Based Redirect"""
    if request.method == 'POST':
        email, password = request.POST.get('email'), request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect(f"{user.role}_dashboard")
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'login.html')


######### Update Profile@login_required
@login_required
def teacher_profile_update(request):
    """Teacher: Update Profile"""
    if request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to update a teacher profile.')
        return redirect('login')

    teacher, created = Teacher.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('teacher_dashboard')
    else:
        form = TeacherProfileForm(instance=teacher)

    return render(request, 'teacher/profile_update.html', {'form': form})


@login_required
def student_profile_update(request):
    """Student: Update Profile"""
    if request.user.role != 'student':
        messages.error(request, 'You do not have permission to update a student profile.')
        return redirect('login')

    student, created = Student.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student, user=request.user)
        if form.is_valid():
            form.save()
            request.user.name = form.cleaned_data['name']
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('student_dashboard')
    else:
        form = StudentProfileForm(instance=student, user=request.user)

    return render(request, 'student/profile_update.html', {'form': form})

### Dashboard Views ###

@login_required
def user_dashboard(request):
    """Redirect to Role-Specific Dashboard"""
    role = request.user.role
    if role == 'superadmin':
        return superadmin_dashboard(request)
    elif role == 'teacher':
        return teacher_dashboard(request)
    elif role == 'student':
        return student_dashboard(request)
    else:
        messages.error(request, 'Invalid role.')
        return redirect('login')


@login_required
def superadmin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')  

    total_users = User.objects.count()
    students_count = User.objects.filter(role='student').count()
    tutors_count = User.objects.filter(role='tutor').count()

    context = {
        'total_users': total_users,
        'students_count': students_count,
        'tutors_count': tutors_count,
    }
    
    return render(request, 'superadmin/dashboard.html', context)


@login_required
def teacher_dashboard(request):
    """Teacher Dashboard: View and Manage Own Homework"""
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    teacher = Teacher.objects.get(user=request.user)
    homeworks = Homework.objects.filter(teacher=teacher).order_by('-posted_date')
    form = TeacherProfileForm(request.POST or None, instance=teacher)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('teacher_dashboard')

    return render(request, 'teacher/dashboard.html', {
        'teacher': teacher,
        'homeworks': homeworks,
        'form': form,
    })


@login_required
def student_dashboard(request):
    """Student Dashboard: View and Submit Homework"""
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    student = Student.objects.get(user=request.user)
    homeworks = Homework.objects.filter(is_active=True)
    submissions = Submission.objects.filter(student=student)
    form = StudentProfileForm(request.POST or None, instance=student)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('student_dashboard')

    return render(request, 'student/dashboard.html', {'homeworks': homeworks, 'submissions': submissions, 'form': form})

# Students List View (Superuser Only)
class StudentsListView(ListView):
    model = User 
    template_name = 'superadmin/students_list.html' 
    context_object_name = 'students'

    def get_queryset(self):
        return User.objects.filter(role='student')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


# Tutors List View (Superuser Only)
class TutorsListView(ListView):
    model = Teacher
    template_name = 'superadmin/tutors_list.html'
    context_object_name = 'teachers' 
    
    def get_queryset(self):
        return Teacher.objects.select_related('user').filter(user__role='teacher')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


# All Users List View (Superuser Only)
class AllUsersListView(ListView):
    model = User
    template_name = 'superadmin/all_users_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.exclude(is_superuser=True)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

# Teacher Profile View
class TeacherProfileView(DetailView):
    model = Teacher
    template_name = 'teacher_profile.html'
    context_object_name = 'teacher'

    def get_object(self):
        return self.request.user.teacher 


class StudentProfileView(DetailView):
    model = Student
    template_name = 'student_profile.html'
    context_object_name = 'student'

    def get_object(self):
        return self.request.user.student


def view_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.role == 'student':
        student = get_object_or_404(Student, user=user)
        return render(request, 'view_user.html', {'user': user, 'student': student})

    elif user.role == 'teacher':
        teacher = get_object_or_404(Teacher, user=user)
        return render(request, 'view_user.html', {'user': user, 'teacher': teacher})

    elif user.role == 'superadmin':
        return render(request, 'view_user.html', {'user': user})
    
    else:
        return render(request, 'view_user.html', {'user': user, 'error': 'Role not recognized'})

### Homework and Submission Management ###

@login_required
def create_homework(request):
    """Teacher: Create New Homework"""
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    form = HomeworkForm(request.POST or None)
    if form.is_valid():
        homework = form.save(commit=False)
        homework.teacher = Teacher.objects.get(user=request.user)
        homework.save()
        messages.success(request, 'Homework created successfully.')
        return redirect('teacher_dashboard')

    return render(request, 'teacher/create_homework.html', {'form': form})


def homework_detail(request, id):
    """View to display the details of a specific homework assignment."""
    homework = get_object_or_404(Homework, id=id)  # Get homework by ID
    return render(request, 'teacher/detail.html', {'homework': homework})


@login_required
def submit_homework(request, homework_id):
    """Student: Submit Homework"""
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    homework = get_object_or_404(Homework, id=homework_id)
    student = Student.objects.get(user=request.user)
    form = SubmissionForm(request.POST, request.FILES)
    
    if form.is_valid():
        submission = form.save(commit=False)
        submission.homework, submission.student = homework, student
        submission.save()
        messages.success(request, 'Homework submitted successfully.')
        return redirect('student_dashboard')

    return render(request, 'student/submit_homework.html', {'form': form, 'homework': homework})

@login_required
def grade_submission(request, submission_id):
    """Teacher: Grade a Student's Submission"""
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    submission = get_object_or_404(Submission, id=submission_id, homework__teacher__user=request.user)
    form = SubmissionForm(request.POST or None, instance=submission)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Grade assigned successfully.')
        return redirect('teacher_dashboard')

    return render(request, 'teacher/grade_submission.html', {'form': form, 'submission': submission})



# 4. Teacher: View Created Homeworks
@login_required
def teacher_homework_list(request):
    """Teacher: List Created Homeworks"""
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    teacher = Teacher.objects.get(user=request.user)
    homeworks = Homework.objects.filter(teacher=teacher)
    return render(request, 'teacher/teacher_homework_list.html', {'homeworks': homeworks})

# 5. Student: View Assigned Homeworks
@login_required
def student_homework_list(request):
    """Student: List Assigned Homeworks"""
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('login')

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('login')
    homeworks = Homework.objects.filter(submissions__student=student)

    return render(request, 'student/student_homework_list.html', {'homeworks': homeworks})

#  Student: View Homework Grades
@login_required
def student_grades_list(request):
    """Student: List Homework Grades"""
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    student = Student.objects.get(user=request.user)
    submissions = Submission.objects.filter(student=student)
    return render(request, 'student/student_grades_list.html', {'submissions': submissions})

#  Teacher: View Submissions for a Homework
@login_required
def homework_submissions_list(request, homework_id):
    """Teacher: List Submissions for a Homework"""
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    homework = get_object_or_404(Homework, id=homework_id, teacher__user=request.user)
    submissions = Submission.objects.filter(homework=homework)
    return render(request, 'teacher/homework_submissions_list.html', {'submissions': submissions, 'homework': homework})

@login_required
def submit_homework(request, homework_id):
    """Student: Submit Homework"""
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    homework = get_object_or_404(Homework, id=homework_id)
    student = Student.objects.get(user=request.user)
    form = SubmissionForm(request.POST, request.FILES)
    
    if form.is_valid():
        submission = form.save(commit=False)
        submission.homework, submission.student = homework, student
        submission.save()
        messages.success(request, 'Homework submitted successfully.')
        return redirect('student_dashboard')

    return render(request, 'student/submit_homework.html', {'form': form, 'homework': homework})


@login_required
def grade_submission(request, submission_id):
    """Teacher: Grade a Student's Submission"""
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    submission = get_object_or_404(Submission, id=submission_id, homework__teacher__user=request.user)
    form = SubmissionForm(request.POST or None, instance=submission)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Grade assigned successfully.')
        return redirect('teacher_dashboard')

    return render(request, 'teacher/grade_submission.html', {'form': form, 'submission': submission})


@login_required
def superadmin_manage_user(request, user_id):
    """Superadmin: Manage User (Edit/Delete)"""
    if request.user.role != 'superadmin':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST' and 'delete' in request.POST:
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('superadmin_dashboard')

    return render(request, 'superadmin/manage_user.html', {'user': user})


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.delete()
        return redirect('all_users_list')
    return render(request, 'confirm_delete.html', {'user': user})


def logout_view(request):
    """User Logout"""
    logout(request)
    return redirect('login')
