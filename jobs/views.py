from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Job
from .forms import JobForm
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse


@login_required
def jobs(request):
    jobs = Job.objects.all().order_by('-posted_at')
    query = request.GET.get("q")

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(location__icontains=query)
        ).distinct()

    if request.GET.get("ajax"):
        html = render_to_string("partials/search_jobs.html", {"jobs": jobs})
        return HttpResponse(html)

    return render(request, "jobs/jobs.html", {"jobs": jobs})




@login_required
def add_job(request):
    if request.user.role != 'alumni' and not request.user.is_superuser:
        messages.error(request, "Only alumni or superusers can post jobs.")
        return redirect('jobs:jobs')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.author = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('jobs:jobs')
    else:
        form = JobForm()

    return render(request, 'jobs/add_job.html', {'form': form})


@login_required
def edit_job(request, job_id):
    """Allow only the author or superuser to edit a job post."""
    job = get_object_or_404(Job, id=job_id)

    if request.user != job.author and not request.user.is_superuser:
        messages.error(request, "You do not have permission to edit this job.")
        return redirect('jobs:jobs')

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('jobs:jobs')
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})


@login_required
def delete_job(request, job_id):
    """Allow only the author or superuser to delete a job post."""
    job = get_object_or_404(Job, id=job_id)

    if request.user != job.author and not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete this job.")
        return redirect('jobs:jobs')

    job.delete()
    messages.success(request, "Job deleted successfully!")
    return redirect('jobs:jobs')


@login_required
def live_search_jobs(request):
    query = request.GET.get('q', '')
    jobs = Job.objects.all().order_by('-posted_at')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(location__icontains=query)
        )

    html = render_to_string('partials/job_list.html', {'jobs': jobs})
    return HttpResponse(html)
