from django.urls import path
from . import views

app_name = 'network'

urlpatterns = [
    path('', views.alumni_directory, name='alumni_directory'),

    path('live_search_users/', views.live_search_users, name='live_search_users'),

]