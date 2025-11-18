from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.jobs, name='jobs'),
    path('add/', views.add_job, name='add_job'),
    path('edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path('delete/<int:job_id>/', views.delete_job, name='delete_job'),

    path('live_search_jobs/', views.live_search_jobs, name='live_search_jobs'),

]
