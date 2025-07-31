from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job, Application
from .forms import JobForm, ApplicationForm

def home(request):
    return render(request, 'jobs/home.html')

def job_list(request):
    query = request.GET.get('q', '')
    jobs = Job.objects.all()
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company_name__icontains=query) |
            Q(location__icontains=query)
        )
    return render(request, 'jobs/job_list.html', {'jobs': jobs, 'query': query})

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'jobs/job_detail.html', {'job': job})

@login_required
def job_create(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_employer:
        messages.error(request, "Only employers can post jobs.")
        return redirect('jobs:home')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('jobs:employer_dashboard')
    else:
        form = JobForm()
    return render(request, 'jobs/job_form.html', {'form': form})

@login_required
def job_apply(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if hasattr(request.user, 'profile') and request.user.profile.is_employer:
        messages.error(request, "Employers cannot apply for jobs.")
        return redirect('jobs:home')
    
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.error(request, "You have already applied for this job.")
        return redirect('jobs:job_detail', pk=pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('jobs:applicant_dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/application_form.html', {'form': form, 'job': job})

@login_required
def employer_dashboard(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_employer:
        messages.error(request, "Access restricted to employers.")
        return redirect('jobs:home')
    
    jobs = Job.objects.filter(posted_by=request.user)
    return render(request, 'jobs/employer_dashboard.html', {'jobs': jobs})

@login_required
def applicant_dashboard(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_employer:
        messages.error(request, "Access restricted to applicants.")
        return redirect('jobs:home')
    
    status = request.GET.get('status', '')
    applications = Application.objects.filter(applicant=request.user)
    if status:
        applications = applications.filter(status=status.upper())
    
    return render(request, 'jobs/applicant_dashboard.html', {
        'applications': applications,
        'status': status
    })

@login_required
def job_applicants(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.posted_by != request.user:
        messages.error(request, "You are not authorized to view these applicants.")
        return redirect('jobs:employer_dashboard')
    
    applications = job.applications.all()
    return render(request, 'jobs/applicants_list.html', {'job': job, 'applications': applications})

@login_required
def update_application_status(request, pk, status):
    application = get_object_or_404(Application, pk=pk)
    if application.job.posted_by != request.user:
        messages.error(request, "You are not authorized to modify this application.")
        return redirect('jobs:employer_dashboard')
    
    if status in ['APPROVED', 'REJECTED']:
        application.status = status
        application.save()
        messages.success(request, f"Application {status.lower()} successfully!")
    else:
        messages.error(request, "Invalid status update.")
    
    return redirect('jobs:job_applicants', pk=application.job.pk)