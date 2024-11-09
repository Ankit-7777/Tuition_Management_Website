from django.urls import path
from . import views
from .views import StudentsListView, TutorsListView, AllUsersListView, delete_user
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    # List Views
    path('users/', AllUsersListView.as_view(), name='all_users_list'),  # All users list view
    path('students/', StudentsListView.as_view(), name='students_list'),  # Students list view
    path('tutors/', TutorsListView.as_view(), name='tutors_list'),  # Tutors list view
    
    
     # Teacher URLs
    path('teacher/homework/', views.teacher_homework_list, name='teacher_homework_list'),
    path('teacher/homework/<int:homework_id>/submissions/', views.homework_submissions_list, name='homework_submissions_list'),

    # Student URLs
    path('student/homework/', views.student_homework_list, name='student_homework_list'),
    path('student/grades/', views.student_grades_list, name='student_grades_list'),


    # Authentication Views
    path('signup/', views.signup_view, name='signup'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # View Profile Pages
    path('user/<int:user_id>/', views.view_user, name='view_user'),
    
    # Profile update based on user role
    path('teacher/profile/update/', views.teacher_profile_update, name='teacher_profile_update'),
    path('student/profile/update/', views.student_profile_update, name='student_profile_update'),


    # Dashboard Views
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('superadmin/dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

    # Homework and Submission Management
    path('homework/create/', views.create_homework, name='create_homework'),
    path('homework/submit/<int:homework_id>/', views.submit_homework, name='submit_homework'),
    path('submission/grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('homework/<int:id>/', views.homework_detail, name='homework_detail'),

    # Superadmin Manage User
    path('superadmin/manage_user/<int:user_id>/', views.superadmin_manage_user, name='superadmin_manage_user'),
    path('user/<int:user_id>/delete/', delete_user, name='delete_user'),  # Delete user

    
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



