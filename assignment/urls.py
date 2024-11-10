from django.urls import path
from . import views
from .views import StudentsListView, TeachersListView, AllUsersListView, delete_user
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    # Authentication and Onboarding
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    
    # Profile Management
    path('teacher/profile/update/', views.teacher_profile_update, name='teacher_profile_update'),
    path('student/profile/update/', views.student_profile_update, name='student_profile_update'),
    path('teacher/profile/', views.TeacherProfileView.as_view(), name='teacher_profile'),
    path('student/profile/', views.StudentProfileView.as_view(), name='student_profile'),

    
    # Dashboard and Navigation
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
     

    # Homework and Assignment Management
    path('homework/create/', views.create_homework, name='create_homework'),
    path('homework/<int:id>/', views.homework_detail, name='homework_detail'),
    path('teacher/homework/list/', views.teacher_homework_list, name='teacher_homework_list'),
    path('student/homework/list/', views.student_homework_list, name='student_homework_list'),
    path('homework/<int:homework_id>/submit/', views.submit_homework, name='submit_homework'),
    path('homework/<int:homework_id>/assign/', views.assign_homework, name='assign_homework'),
    path('homework/<int:homework_id>/submissions/', views.homework_submissions_list, name='homework_submissions_list'),

    # Submissions and Grading
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('student/grades/', views.student_grades_list, name='student_grades_list'),


     # Superadmin Management
    path('superadmin/students/', views.StudentsListView.as_view(), name='students_list'),
    path('superadmin/teachers/', views.TeachersListView.as_view(), name='tutors_list'),
    path('superadmin/users/', views.AllUsersListView.as_view(), name='all_users_list'),
    path('superadmin/user/<int:user_id>/', views.view_user, name='view_user'),
    path('superadmin/user/<int:user_id>/manage/', views.superadmin_manage_user, name='superadmin_manage_user'),
    path('user/<int:user_id>/delete/', delete_user, name='delete_user'), 

    
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



