from django.utils import timezone
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate

from .models import CustomUser, Job, JobApplication, Notification
import json


# ---------------------------------------------------------
# BASIC PAGES
# ---------------------------------------------------------

def job_detail_page(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, "core/job.html", {"job": job})


def home_view(request):
    return render(request, 'core/home.html')


def freelancer_auth_view(request):
    return render(request, 'core/freelancer_auth.html')


def recruiter_auth_view(request):
    return render(request, 'core/recruiter_auth.html')


def freelancer_dashboard(request):
    username = request.GET.get('username', 'Freelancer')
    return render(request, 'core/freelancer_dashboard.html', {'username': username})


def recruiter_dashboard(request):
    username = request.GET.get('username', 'Recruiter')
    return render(request, 'core/recruiter_dashboard.html', {'username': username})


# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """
    FIXED SIGNUP:
    - Accepts username, password, role, email (email optional for recruiters)
    - Creates CustomUser correctly
    """
    username = request.data.get('username')
    password = request.data.get('password')
    role = request.data.get('role', 'freelancer')
    email = request.data.get('email', "")  # optional

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=400)

    if CustomUser.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)

    CustomUser.objects.create_user(
        username=username,
        password=password,
        role=role,
        email=email
    )
    return Response({'message': f'{role.capitalize()} account created successfully!'}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def signin_view(request):
    """
    FIXED SIGNIN:
    - Uses Django authenticate()
    - Verifies username + password correctly
    - Redirects based on user.role
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Both fields required'}, status=400)

    user = authenticate(username=username, password=password)

    if not user:
        return Response({'error': 'Invalid username or password'}, status=400)

    # Determine redirect URL
    redirect_url = (
        f'/freelancer/dashboard/?username={username}'
        if user.role == 'freelancer'
        else f'/recruiter/dashboard/?username={username}'
    )

    return Response({'role': user.role, 'redirect_url': redirect_url}, status=200)


# ---------------------------------------------------------
# JOB CREATION & LISTING
# ---------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def create_job_view(request):
    recruiter_username = request.data.get('recruiter_username')
    title = request.data.get('title')
    pay_per_hour = request.data.get('pay_per_hour')
    tech_stack = request.data.get('tech_stack')
    experience_level = request.data.get('experience_level')
    description = request.data.get('description', '')

    if not recruiter_username or not title:
        return Response({'error': 'Missing required fields'}, status=400)

    try:
        recruiter = CustomUser.objects.get(username=recruiter_username, role='recruiter')
    except CustomUser.DoesNotExist:
        return Response({'error': 'Recruiter not found'}, status=404)

    job = Job.objects.create(
        recruiter=recruiter,
        title=title,
        pay_per_hour=pay_per_hour or 0,
        tech_stack=tech_stack or '',
        experience_level=experience_level,
        description=description,
    )
    return Response({'message': 'Job created successfully', 'job_id': job.id})


@api_view(['GET'])
@permission_classes([AllowAny])
def job_list_view(request):
    jobs = Job.objects.all().order_by('-created_at')

    return Response([
        {
            'id': job.id,
            'title': job.title,
            'pay_per_hour': str(job.pay_per_hour),
            'tech_stack': job.tech_stack,
            'experience_level': job.experience_level,
            'description': job.description,
            'recruiter': job.recruiter.username,
        }
        for job in jobs
    ])


# ---------------------------------------------------------
# JOB APPLICATIONS
# ---------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def apply_to_job_view(request, job_id):
    username = request.data.get('username')

    try:
        freelancer = CustomUser.objects.get(username=username, role='freelancer')
    except CustomUser.DoesNotExist:
        return Response({'error': 'Freelancer not found'}, status=404)

    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'error': 'Job not found'}, status=404)

    # Prevent duplicate applications
    if JobApplication.objects.filter(job=job, freelancer=freelancer).exists():
        return Response({'error': 'Already applied'}, status=400)

    app = JobApplication.objects.create(job=job, freelancer=freelancer)

    # Notification to recruiter
    Notification.objects.create(
        recruiter=job.recruiter,
        message=f"{freelancer.username} applied for '{job.title}'"
    )

    return Response({'message': 'Application submitted successfully', 'application_id': app.id})


@api_view(['GET'])
def view_applications(request, job_id):
    apps = JobApplication.objects.filter(job_id=job_id)

    return Response([
        {
            'application_id': a.id,
            'freelancer': a.freelancer.username,
            'status': a.status,
            'applied_at': a.applied_at.strftime("%Y-%m-%d %H:%M"),
        }
        for a in apps
    ])


@api_view(["POST"])
def update_application_status(request, application_id):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    new_status = data.get("status")
    if not new_status:
        return JsonResponse({"error": "Status is required"}, status=400)

    try:
        application = JobApplication.objects.get(id=application_id)
    except JobApplication.DoesNotExist:
        return JsonResponse({"error": "Application not found"}, status=404)

    application.status = new_status
    application.save()

    # Email freelancer
    freelancer_email = application.freelancer.email
    job_title = application.job.title

    if freelancer_email:
        send_mail(
            subject="Your Application Status Updated",
            message=(
                f"Hello {application.freelancer.username},\n\n"
                f"Your application for the job '{job_title}' "
                f"has been updated to: {new_status.upper()}.\n\n"
                f"Regards,\nSkillConnect Team"
            ),
            from_email="skillconnect@example.com",
            to=[freelancer_email],
            fail_silently=True
        )

    return JsonResponse({"message": "Status updated and email sent successfully"})


# ---------------------------------------------------------
# FREELANCER APPLICATION HISTORY
# ---------------------------------------------------------

@api_view(['GET'])
def my_applications(request, freelancer_username):
    apps = JobApplication.objects.filter(freelancer__username=freelancer_username)

    return Response([
        {
            'job_title': a.job.title,
            'status': a.status,
            'applied_at': a.applied_at.strftime("%Y-%m-%d %H:%M")
        }
        for a in apps
    ])


# ---------------------------------------------------------
# RECRUITER APPLICATIONS
# ---------------------------------------------------------

@api_view(['GET'])
def recruiter_job_applications(request, recruiter_username):
    try:
        recruiter = CustomUser.objects.get(username=recruiter_username, role='recruiter')
    except CustomUser.DoesNotExist:
        return Response({'error': 'Recruiter not found'}, status=404)

    jobs = Job.objects.filter(recruiter=recruiter)
    response = []

    for job in jobs:
        apps = JobApplication.objects.filter(job=job)
        response.append({
            'job_title': job.title,
            'job_id': job.id,
            'applications': [
                {
                    'application_id': a.id,
                    'freelancer': a.freelancer.username,
                    'status': a.status,
                    'applied_at': a.applied_at.strftime("%Y-%m-%d %H:%M")
                }
                for a in apps
            ]
        })

    return Response(response)


# ---------------------------------------------------------
# NOTIFICATIONS
# ---------------------------------------------------------

@api_view(['GET'])
def recruiter_notifications(request, recruiter_username):
    try:
        recruiter = CustomUser.objects.get(username=recruiter_username)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Recruiter not found'}, status=404)

    notes = Notification.objects.filter(recruiter=recruiter).order_by('-created_at')

    return Response([
        {
            'id': n.id,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for n in notes
    ])


@api_view(['POST'])
def mark_notifications_read(request, recruiter_username):
    try:
        recruiter = CustomUser.objects.get(username=recruiter_username)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Recruiter not found'}, status=404)

    Notification.objects.filter(recruiter=recruiter, is_read=False).update(is_read=True)
    return Response({'message': 'Notifications marked as read'})
