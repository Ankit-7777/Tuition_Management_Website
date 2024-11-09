from django.contrib import admin
from .models import User, Teacher, Student, Homework, Submission

# Custom user admin for the custom user model
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'role', 'is_staff', 'is_superuser')
    search_fields = ('email', 'name')
    list_filter = ('role', 'is_staff', 'is_superuser')
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)

# Teacher Admin
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'bio', 'profile_picture')
    search_fields = ('user__email', 'user__name', 'department')
    list_filter = ('department',)
    ordering = ('user__email',)

admin.site.register(Teacher, TeacherAdmin)

# Student Admin
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'grade_level', 'bio', 'profile_picture')
    search_fields = ('user__email', 'user__name', 'grade_level')
    list_filter = ('grade_level',)
    ordering = ('user__email',)

admin.site.register(Student, StudentAdmin)

# Homework Admin
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'title', 'subject', 'due_date', 'posted_date', 'is_active')
    search_fields = ('title', 'description', 'teacher__user__email')
    list_filter = ('subject', 'teacher', 'is_active')
    ordering = ('-posted_date',)

admin.site.register(Homework, HomeworkAdmin)

# Submission Admin
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'homework', 'submitted_at', 'grade', 'comments')
    search_fields = ('student__user__email', 'homework__title', 'comments')
    list_filter = ('grade',)
    ordering = ('-submitted_at',)

admin.site.register(Submission, SubmissionAdmin)
