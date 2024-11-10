from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, ListView
from .forms import SignupForm, TeacherProfileForm, StudentProfileForm, HomeworkForm, SubmissionForm
from .models import User, Teacher, Student, Homework, Submission
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden


### 1. Authentication and Onboarding ###

def signup_view(request):
    """User Signup with Role-Based Redirect"""
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


@login_required
def logout_view(request):
    """Logout and Redirect to Login"""
    logout(request)
    return redirect('login')


### 2. Profile Management ###

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
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            # request.user.name = form.cleaned_data['name']
            # request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('student_dashboard')
    else:
        form = StudentProfileForm(instance=student)
    return render(request, 'student/profile_update.html', {'form': form})


class TeacherProfileView(DetailView):
    """View Teacher Profile"""
    model = Teacher
    template_name = 'teacher_profile.html'
    context_object_name = 'teacher'

    def get_object(self):
        return self.request.user.teacher 


class StudentProfileView(DetailView):
    """View Student Profile"""
    model = Student
    template_name = 'student_profile.html'
    context_object_name = 'student'

    def get_object(self):
        return self.request.user.student


### 3. Dashboard and Navigation ###

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
    """Superadmin Dashboard with User Counts"""
    if not request.user.is_superuser:
        return redirect('login')
    total_users = User.objects.count()
    students_count = User.objects.filter(role='student').count()
    teachers_count = User.objects.filter(role='teacher').count()
    context = {
        'total_users': total_users,
        'students_count': students_count,
        'teachers_count': teachers_count,
    }
    return render(request, 'superadmin/dashboard.html', context)


@login_required
def teacher_dashboard(request):
    """Teacher Dashboard with Homework Listings"""
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    teacher = Teacher.objects.get(user=request.user)
    homeworks = Homework.objects.filter(teacher=teacher).order_by('-posted_date')
    return render(request, 'teacher/dashboard.html', {
        'teacher': teacher,
        'homeworks': homeworks
    })


@login_required
def student_dashboard(request):
    """Student Dashboard with Assigned Homeworks and Submissions"""
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    student = Student.objects.get(user=request.user)
    homeworks = Homework.objects.filter(is_active=True)
    submissions = Submission.objects.filter(student=student)
    return render(request, 'student/dashboard.html', {
        'homeworks': homeworks,
        'submissions': submissions
    })


### 4. Homework and Assignment Management ###

@login_required
def create_homework(request):
    """Teacher: Create Homework"""
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

@login_required
def homework_detail(request, id):
    """View Homework Detail"""
    homework = get_object_or_404(Homework, id=id)
    return render(request, 'teacher/detail.html', {'homework': homework})


@login_required
def teacher_homework_list(request):
    """View the list of homework assigned by the teacher."""
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    teacher = request.user.teacher  # Assuming Teacher is a one-to-one with User
    homeworks = Homework.objects.filter(teacher=teacher)
    return render(request, 'teacher/teacher_homework_list.html', {'homeworks': homeworks})


@login_required
def student_homework_list(request):
    """Student: View Assigned Homeworks"""
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('login')

    student = Student.objects.get(user=request.user)
    homeworks = Homework.objects.filter(submissions__student=student).distinct()
    return render(request, 'student/student_homework_list.html', {'homeworks': homeworks})


### 5. Submissions and Grading ###

@login_required
def submit_homework(request, homework_id):
    """Student: Submit Homework"""
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    homework = get_object_or_404(Homework, id=homework_id)
    student = Student.objects.get(user=request.user)

    # Check if the student has already submitted this homework
    if Submission.objects.filter(homework=homework, student=student).exists():
        messages.error(request, 'You have already submitted this homework.')
        return redirect('student_dashboard')
    
    form = SubmissionForm(request.POST, request.FILES)
    if form.is_valid():
        submission = form.save(commit=False)
        submission.homework = homework
        submission.student = student
        submission.save()
        messages.success(request, 'Homework submitted successfully.')
        return redirect('student_dashboard')
    
    return render(request, 'student/submit_homework.html', {'form': form, 'homework': homework})


@login_required
def assign_homework(request, homework_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    homework = get_object_or_404(Homework, pk=homework_id)
    students = Student.objects.all()

    if request.method == 'POST':
        selected_students = request.POST.getlist('students')
        homework.assigned_students.set(selected_students)
        return redirect('teacher_homework_list')

    return render(request, 'teacher/assign_homework.html', {'homework': homework, 'students': students})


@login_required
def homework_submissions_list(request, homework_id):
    """Teacher: List Submissions for a Homework"""
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    homework = get_object_or_404(Homework, pk=homework_id, teacher=request.user.teacher)
    submissions = homework.submissions.all()
    return render(request, 'teacher/homework_submissions_list.html', {'submissions': submissions, 'homework': homework})


@login_required
def grade_submission(request, submission_id):
    """Teacher: Grade Submission"""
    if request.user.role != 'teacher':
        messages.error(request, 'Permission denied.')
        return redirect('login')
    
    submission = get_object_or_404(Submission, pk=submission_id, homework__teacher__user=request.user)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade assigned successfully.')
            return redirect('teacher_homework_list')
    else:
        form = SubmissionForm(instance=submission)
    return render(request, 'teacher/grade_submission.html', {'form': form, 'submission': submission})


@login_required
def student_grades_list(request):
    """Student: List Grades"""
    if request.user.role != 'student':
        messages.error(request, 'Permission denied.')
        return redirect('login')

    student = Student.objects.get(user=request.user)
    submissions = Submission.objects.filter(student=student).select_related('homework')
    return render(request, 'student/student_grades_list.html', {'submissions': submissions})


### 6. Superadmin Management ###
class SuperadminRequiredMixin(LoginRequiredMixin):
    """Mixin to restrict view access to superadmin users only."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'superadmin':
            messages.error(request, 'Permission denied. Only superadmin can access this page.')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

class StudentsListView(SuperadminRequiredMixin, ListView):
    """Superadmin: View Students"""
    model = User
    template_name = 'superadmin/students_list.html'
    context_object_name = 'students'
    login_url = 'login'  

    def get_queryset(self):
        students = User.objects.filter(role='student')
        print(students)  # Debugging the queryset
        return students

class TeachersListView(SuperadminRequiredMixin, ListView):
    """Superadmin: View Teachers"""
    model = Teacher
    template_name = 'superadmin/teachers_list.html'
    context_object_name = 'teachers'
    login_url = 'login'

    def get_queryset(self):
        return Teacher.objects.select_related('user').filter(user__role='teacher')

class AllUsersListView(SuperadminRequiredMixin, ListView):
    """Superadmin: View All Users"""
    model = User
    template_name = 'superadmin/all_users_list.html'
    context_object_name = 'users'
    login_url = 'login'

    def get_queryset(self):
        return User.objects.exclude(is_superuser=True)



def view_user(request, user_id):

    email = get_object_or_404(User, pk=user_id)
    try:
        profile = User.objects.get(email=email) 
    except User.DoesNotExist:
        profile = None 
    if not request.user.is_authenticated or request.user.role != 'superadmin':
        return HttpResponseForbidden("You do not have permission to view this profile.")
    return render(request, 'view_user.html', {'email': email, 'profile': profile})

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




