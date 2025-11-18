# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('with/<str:username>/', views.chat_with, name='chat_with'),
    path('fetch/<str:username>/', views.fetch_messages, name='fetch_messages'),

    

]
