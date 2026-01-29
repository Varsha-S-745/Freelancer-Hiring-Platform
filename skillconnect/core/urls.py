from django.urls import path
from . import views

urlpatterns = [

    # Pages
    path('', views.home_view, name='home'),
    path('freelancer/auth/', views.freelancer_auth_view, name='freelancer_auth'),
    path('recruiter/auth/', views.recruiter_auth_view, name='recruiter_auth'),
    path('freelancer/dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('recruiter/dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),

    # Job detail page (missing earlier)
    path("job/<int:job_id>/", views.job_detail_page, name="job_detail_page"),

    # Auth API
    path('api/signup/', views.signup_view, name='signup'),
    path('api/signin/', views.signin_view, name='signin'),

    # Jobs API
    path('api/jobs/create/', views.create_job_view, name='create_job'),
    path('api/jobs/', views.job_list_view, name='list_jobs'),
    path('api/jobs/<int:job_id>/apply/', views.apply_to_job_view, name='apply_job'),
    path('api/jobs/<int:job_id>/applications/', views.view_applications, name='view_applications'),

    # Application status API
    path('api/applications/<int:application_id>/status/', views.update_application_status, name='update_status'),

    # User-specific API
    path('api/freelancer/<str:freelancer_username>/applications/', views.my_applications, name='my_applications'),
    path('api/recruiter/<str:recruiter_username>/applications/', views.recruiter_job_applications, name='recruiter_job_applications'),

    # Notifications API
    path('api/recruiter/<str:recruiter_username>/notifications/', views.recruiter_notifications, name='recruiter_notifications'),
    path('api/recruiter/<str:recruiter_username>/notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
]
