from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # --- Authentication ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),

    # --- Home / Alumni ---
    path('home/', views.home, name='home'),
    path('alumni/', views.alumni_view, name='alumni'),

    # --- Profile pages ---
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('add-experience/', views.add_experience, name='add_experience'),
    path('add-project/', views.add_project, name='add_project'),
    path('add-achievement/', views.add_achievement, name='add_achievement'),

    # --- Posts ---
    path('posts/add/', views.add_post, name='add_post'),
    path('posts/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('posts/delete/<int:post_id>/', views.delete_post, name='delete_post'),

    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("comment/<int:post_id>/", views.add_comment, name="add_comment"),
    path("get_comments/<int:post_id>/", views.get_comments, name="get_comments"),
    path("delete/<int:post_id>/", views.delete_post, name="delete_post"),

    #--- Connections -----
    path('connect/<int:user_id>/', views.send_connection_request, name='send_connection_request'),
    #path('requests/', views.connection_requests, name='connection_requests'),
    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),

    #----Notifications---
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/clear/', views.clear_all_notifications, name='clear_all_notifications'),
    path('notifications/delete/<int:pk>/', views.delete_notification, name='delete_notification'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),


    
    path('privacy-settings/', views.privacy_settings, name='privacy_settings'),


    


    #admin delete users 
    
    path("admin/delete-user/<int:uid>/", views.delete_user, name="delete_user"),
    path("admin/search-users/", views.search_users, name="search_users"),
    path("admin/delete-users/", views.admin_delete_users, name="admin_delete_users"),


    #searchposts
    path("posts/<int:post_id>/comments/", views.post_comments, name="post_comments"),
    path('live_search_posts/', views.live_search_posts, name='live_search_posts'),
    #path('load-comments/<int:post_id>/', views.load_comments, name='load-comments')

    
]
