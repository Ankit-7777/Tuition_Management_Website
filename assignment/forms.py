from django import forms
from .models import User, Homework, Submission, Teacher, Student



ROLE_CHOICES = [
    ('student', 'Student'),
    ('teacher', 'Teacher'),
]

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Role")

    class Meta:
        model = User
        fields = ['email', 'name', 'password1', 'password2', 'role']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Hash the password
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email','name', 'role', 'is_staff', 'is_superuser', 'is_active']




# Teacher Profile Form
class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['user', 'department', 'bio', 'profile_picture']



class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['grade_level', 'bio', 'profile_picture']  
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['name'] = forms.CharField(
                initial=user.name, required=True, label="Name", widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'id': 'id_name'
                })
            )
            self.fields['email'] = forms.EmailField(
                initial=user.email, required=False, disabled=True, label="Email", widget=forms.TextInput(attrs={
                    'class': 'form-control-plaintext',
                    'id': 'id_user'
                })
            )


class HomeworkForm(forms.ModelForm):
    """Form for Homework"""
    class Meta:
        model = Homework
        fields = ['title', 'description', 'subject', 'due_date', 'is_active'] 

    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100%;'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'width: 100%;'}))
    due_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'style': 'width: 100%;', 'type': 'date'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'width: auto;'}))
    subject = forms.ChoiceField(choices=Homework.SUBJECT_CHOICES, widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%;'}))


class SubmissionForm(forms.ModelForm):
    """Form for grading a Homework Submission"""
    class Meta:
        model = Submission
        fields = ['grade', 'comments']

    grade = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter grade',
            'style': 'width: 100%;'
        })
    )

    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Add comments (optional)',
            'style': 'width: 100%;'
        })
    )
