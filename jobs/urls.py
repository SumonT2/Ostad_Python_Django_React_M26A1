from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/new/', views.job_create, name='job_create'),
    path('job/<int:pk>/apply/', views.job_apply, name='job_apply'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('applicant/dashboard/', views.applicant_dashboard, name='applicant_dashboard'),
    path('job/<int:pk>/applicants/', views.job_applicants, name='job_applicants'),
    path('application/<int:pk>/status/<str:status>/', views.update_application_status, name='update_application_status'),
]