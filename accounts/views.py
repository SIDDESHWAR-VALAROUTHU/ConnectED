from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponseForbidden
from .models import Project, Experience, Achievement, CustomUser, Post, PostView ,Like, Comment,Connection, PrivacySettings,Notification
from django.utils import timezone
import random
from django.db import models
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse


from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    ProjectForm,
    ExperienceForm,
    AchievementForm,
)

User = get_user_model()


# -------------------------------
# REGISTER VIEW (Admin only)
# -------------------------------
@login_required
def register_view(request):
    # Restrict registration to superusers (admins)
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('accounts:home')

    if request.method == 'POST':
        uid = request.POST.get('uid', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()
        department = request.POST.get('department', '').strip()
        batch = request.POST.get('batch', '').strip()
        role = request.POST.get('role', '').strip()

        # ✅ Validation checks
        if not uid or not email or not username or not password1 or not password2 or not department or not batch or not role:
            messages.error(request, "All fields are required.")
            return render(request, 'accounts/register.html')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html')

        if CustomUser.objects.filter(uid=uid).exists():
            messages.error(request, "User ID (UID) already exists. Please choose another.")
            return render(request, 'accounts/register.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered. Try logging in or use another email.")
            return render(request, 'accounts/register.html')

        # ✅ Create new user
        user = CustomUser.objects.create_user(
            uid=uid,
            email=email,
            username=username,
            password=password1,
            department=department,
            batch=batch,
            role=role,
        )

        messages.success(request, f"Account for '{username}' created successfully!")
        return redirect('accounts:login')

    return render(request, 'accounts/register.html')

# -------------------------------
# LOGIN VIEW
# -------------------------------
def login_view(request):
    """Handles user login — first page of the site."""
    if request.user.is_authenticated:
        return redirect('accounts:profile', username=request.user.username)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('accounts:profile', username=user.username)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')


# -------------------------------
# LOGOUT VIEW
# -------------------------------
@login_required
def logout_view(request):
    """Logs out the user and redirects to login page."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')


# -------------------------------
# PROFILE VIEW
# -------------------------------
from django.db.models import Q

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = (profile_user == request.user)

    # Get actual connection object (not just True/False)
    connection = Connection.objects.filter(
        Q(from_user=request.user, to_user=profile_user) |
        Q(from_user=profile_user, to_user=request.user)
    ).first()

    connections = Connection.objects.filter(
        Q(from_user=profile_user) | Q(to_user=profile_user),
        status='accepted'
    )
    # Determine connection status for privacy logic
    is_connected = connection and connection.status == 'accepted'

    privacy = getattr(profile_user, 'privacy', None)

    # Hide restricted data for non-connected users
    hide_experience = privacy and not privacy.show_experience and not is_own_profile and not is_connected
    hide_projects = privacy and not privacy.show_projects and not is_own_profile and not is_connected
    hide_achievements = privacy and not privacy.show_achievements and not is_own_profile and not is_connected
    hide_posts = privacy and not privacy.show_posts and not is_own_profile and not is_connected
    hide_contact = privacy and not privacy.show_contact_info and not is_own_profile and not is_connected
    
    profile_pic_url = (
        profile_user.profile_pic.url
        if profile_user.profile_pic and hasattr(profile_user.profile_pic, 'url')
        else "https://via.placeholder.com/150"
    )
    cover_pic_url = (
        profile_user.cover_pic.url
        if profile_user.cover_pic and hasattr(profile_user.cover_pic, 'url')
        else "https://images.unsplash.com/photo-1503264116251-35a269479413?auto=format&fit=crop&w=1350&q=80"
    )

    experiences = [] if hide_experience else Experience.objects.filter(user=profile_user)
    projects = [] if hide_projects else Project.objects.filter(user=profile_user)
    achievements = [] if hide_achievements else Achievement.objects.filter(user=profile_user)
    posts = [] if hide_posts else Post.objects.filter(author=profile_user)

    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'profile_pic_url': profile_pic_url,
        'cover_pic_url': cover_pic_url,
        'experiences': experiences,
        'projects': projects,
        'achievements': achievements,
        'posts': posts,
        'hide_contact': hide_contact,
        'privacy': privacy,
        'connection': connection,  # <-- key fix    
        'connections': connections,
    })



# -------------------------------
# EDIT PROFILE
# -------------------------------
@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user.email = request.POST.get('email')
        user.department = request.POST.get('department')
        user.batch = request.POST.get('batch')
        user.location = request.POST.get('location')
        user.current_designation = request.POST.get('current_designation')
        user.company = request.POST.get('company')
        user.about = request.POST.get('about')
        user.contact_number = request.POST.get('contact_number')

        if 'profile_pic' in request.FILES:
            user.profile_pic = request.FILES['profile_pic']
        if 'cover_pic' in request.FILES:
            user.cover_pic = request.FILES['cover_pic']

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('accounts:profile', username=user.username)

    return render(request, 'accounts/edit_profile.html', {'user': user})


# -------------------------------
# EXPERIENCE, PROJECT, ACHIEVEMENT
# -------------------------------
@login_required
def add_experience(request):
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = ExperienceForm()
    return render(request, 'accounts/add_experience.html', {'form': form})


@login_required
def add_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, "Project added successfully!")
            return redirect("accounts:profile", username=request.user.username)
    else:
        form = ProjectForm()
    return render(request, "accounts/add_project.html", {"form": form})


@login_required
def add_achievement(request):
    if request.method == "POST":
        form = AchievementForm(request.POST)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.user = request.user
            achievement.save()
            messages.success(request, "Achievement added successfully!")
            return redirect("accounts:profile", username=request.user.username)
    else:
        form = AchievementForm()
    return render(request, "accounts/add_achievement.html", {"form": form})


# -------------------------------
# POST CRUD
# -------------------------------
@login_required
def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        Post.objects.create(author=request.user, title=title, description=description, image=image)
        return redirect('accounts:profile', username=request.user.username)
    return render(request, 'accounts/add_post.html')


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You can't edit this post.")
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.description = request.POST.get('description')
        if request.FILES.get('image'):
            post.image = request.FILES.get('image')
        post.save()
        return redirect('accounts:profile', username=post.author.username)
    return render(request, 'accounts/edit_post.html', {'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You can't delete this post.")
    if request.method == 'POST':
        post.delete()
        return redirect('accounts:profile', username=request.user.username)
    return render(request, 'accounts/confirm_delete_post.html', {'post': post})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'accounts/post_detail.html', {'post': post})




@login_required
def home(request):
    user = request.user

    # Get connected users (both sides accepted)
    connections = Connection.objects.filter(
        (Q(from_user=user) | Q(to_user=user)),
        status="accepted"
    )

    connected_users = set()
    for c in connections:
        if c.from_user == user:
            connected_users.add(c.to_user)
        else:
            connected_users.add(c.from_user)

    # STEP 1: Fetch all posts except user's own
    posts = Post.objects.exclude(author=user)

    # STEP 2: Apply privacy filtering
    visible_posts = []
    for post in posts:
        privacy = getattr(post.author, "privacy", None)

        # If author has no privacy settings, treat as public
        if privacy is None or privacy.show_posts:
            visible_posts.append(post)
        else:
            # show_posts = False → only connected users can see
            if post.author in connected_users:
                visible_posts.append(post)

    posts = Post.objects.filter(id__in=[p.id for p in visible_posts])

    # STEP 3: Apply search
    query = request.GET.get("q")
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).distinct()

    # AJAX partial
    if request.GET.get("ajax"):
        html = render_to_string("partials/search_posts.html", {"posts": posts})
        return HttpResponse(html)

    # STEP 4: Seen/unseen logic
    seen_post_ids = PostView.objects.filter(user=user).values_list('post_id', flat=True)
    unseen_posts = posts.exclude(id__in=seen_post_ids)

    if unseen_posts.count() < 5:
        remaining_needed = 10 - unseen_posts.count()
        seen_posts = posts.filter(id__in=seen_post_ids).order_by('?')[:remaining_needed]
        posts_to_show = list(unseen_posts) + list(seen_posts)
    else:
        posts_to_show = list(unseen_posts)

    random.shuffle(posts_to_show)

    # Add like/comment flags
    for post in posts_to_show:
        PostView.objects.get_or_create(user=user, post=post)
        post.is_liked = Like.objects.filter(post=post, user=user).exists()
        post.likes_count = Like.objects.filter(post=post).count()
        post.comments_count = Comment.objects.filter(post=post).count()

    return render(request, "accounts/home.html", {"posts": posts_to_show})



@login_required
@csrf_exempt
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user

    like, created = Like.objects.get_or_create(post=post, user=user)

    if not created:
        # If already liked, unlike it
        like.delete()
        liked = False
    else:
        liked = True

    like_count = post.likes.count()
    return JsonResponse({'liked': liked, 'like_count': like_count})


@login_required
def get_comments(request, post_id):
    post = Post.objects.get(id=post_id)
    comments = post.comments.all().order_by('-created_at')
    return JsonResponse({'comments': [
        {'author': c.user.username, 'text': c.content} for c in comments
    ]})

@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        text = request.POST.get('text', '').strip()
        post = Post.objects.get(id=post_id)
        if text:
            comment = Comment.objects.create(post=post, user=request.user, content=text)
            return JsonResponse({'author': comment.user.username, 'text': comment.content})
    return JsonResponse({'error': 'Invalid comment'}, status=400)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required



# ---------- SEND REQUEST ----------
@login_required
def send_connection_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)

    if to_user == request.user:
        messages.error(request, "You cannot send a connection request to yourself.")
        return redirect('accounts:profile_view', username=to_user.username)

    existing_request = Connection.objects.filter(from_user=request.user, to_user=to_user).first()

    if existing_request:
        if existing_request.status == 'rejected':
            existing_request.delete()
            Connection.objects.create(from_user=request.user, to_user=to_user, status='pending')
            messages.success(request, f"Connection request sent again to {to_user.username}.")
        elif existing_request.status == 'pending':
            messages.info(request, "Connection request is already pending.")
        elif existing_request.status == 'accepted':
            messages.info(request, "You are already connected.")
    else:
        connection = Connection.objects.create(from_user=request.user, to_user=to_user, status='pending')

        # ✅ Create a notification for the receiver
        Notification.objects.create(
            user=to_user,                   # who receives the notification
            from_user=request.user,         # who triggered it
            message=f"{request.user.username} sent you a connection request.",
            notification_type='connection', # optional tag for filtering later
            connection=connection           # link this notification to that connection
        )
        messages.success(request, f"Connection request sent to {to_user.username}.")

    # ✅ Redirect based on where the request came from
    referer = request.META.get('HTTP_REFERER', '')

    if 'network' in referer:
        # Redirect back to the alumni directory (network page)
        return redirect('network:alumni_directory')
    else:
        # Default redirect — back to the user's profile page
        return redirect('accounts:profile', username=to_user.username)




# ---------- VIEW PENDING REQUESTS ----------
'''
@login_required
def connection_requests(request):
    pending_requests = Connection.objects.filter(to_user=request.user, status='pending')
    return render(request, 'accounts/connection_requests.html', {'pending_requests': pending_requests})
'''

# ---------- ACCEPT REQUEST ----------
@login_required
def accept_request(request, request_id):
    """Accept a connection request and clean up old notifications."""
    connection = get_object_or_404(Connection, id=request_id, to_user=request.user)

    # Update connection status
    connection.status = 'accepted'
    connection.save()

    # Delete any old pending notifications about this same request
    Notification.objects.filter(connection=connection, user=request.user).delete()

    # Notify the sender that their request was accepted
    Notification.objects.create(
        user=connection.from_user,
        from_user=request.user,
        message=f"{request.user.username} accepted your connection request.",
        notification_type='connection',
        connection=connection
    )

    messages.success(request, f"You are now connected with {connection.from_user.username}.")
    return redirect('accounts:notifications')


@login_required
def reject_request(request, request_id):
    """Reject a connection request and clean up old notifications."""
    connection = get_object_or_404(Connection, id=request_id, to_user=request.user)

    # Update status
    connection.status = 'rejected'
    connection.save()

    # Delete any old pending notifications about this same request
    Notification.objects.filter(connection=connection, user=request.user).delete()

    # Notify sender that their request was rejected
    Notification.objects.create(
        user=connection.from_user,
        from_user=request.user,
        message=f"{request.user.username} rejected your connection request.",
        notification_type='connection',
        connection=connection
    )

    messages.info(request, f"Connection request from {connection.from_user.username} rejected.")
    return redirect('accounts:notifications')



from django.db.models import Q
from django.utils import timezone
from itertools import chain
from operator import attrgetter
from django.urls import reverse

@login_required
def notifications_view(request):
    """
    Unified notifications feed with no duplicates.
    Shows dynamic connection requests (Accept/Reject) only when pending
    and removes them once accepted or rejected.
    """
    from django.db.models import Q

    # Get all saved notifications
    db_notifications = list(
        Notification.objects.filter(user=request.user)
        .select_related('from_user', 'connection')
        .order_by('-timestamp')
    )

    # Track which connection IDs already have notifications
    existing_connection_ids = {
        n.connection.id for n in db_notifications if n.connection_id
    }

    # Fetch all pending connection requests for this user
    pending_connections = Connection.objects.filter(
        to_user=request.user, status='pending'
    )

    dynamic_notifications = []
    for conn in pending_connections:
        # Only show if a Notification for this connection doesn’t already exist
        if conn.id not in existing_connection_ids:
            dynamic_notifications.append({
                'from_user': conn.from_user,
                'message': f"{conn.from_user.username} sent you a connection request.",
                'timestamp': getattr(conn, 'created_at', timezone.now()),
                'action': {
                    'request_id': conn.id,
                    'accept_url': reverse('accounts:accept_request', args=[conn.id]),
                    'reject_url': reverse('accounts:reject_request', args=[conn.id]),
                },
                'is_dynamic': True,
            })

    # Combine database + dynamic notifications
    notifications = dynamic_notifications + db_notifications

    # Mark all unread notifications as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    # Sort all notifications (dicts + model objects)
    notifications.sort(
    key=lambda n: n.timestamp if hasattr(n, 'timestamp') else n['timestamp'],
    reverse=True
    )

    return render(request, 'accounts/notifications.html', {'notifications': notifications})


@login_required
def clear_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    Connection.objects.filter(from_user=request.user, status='accepted').delete()
    Connection.objects.filter(to_user=request.user, status='pending').delete()
    messages.success(request, "All notifications cleared.")
    return redirect('accounts:notifications')



@login_required
def delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    if request.method == 'POST':
        notification.delete()
        return redirect('accounts:notifications')
    return redirect('accounts:notifications')


@login_required
def clear_notifications(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user).delete()
    return redirect('accounts:notifications')


@login_required
def privacy_settings(request):
    privacy, created = PrivacySettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        privacy.show_experience = 'show_experience' in request.POST
        privacy.show_projects = 'show_projects' in request.POST
        privacy.show_achievements = 'show_achievements' in request.POST
        privacy.show_posts = 'show_posts' in request.POST
        privacy.show_contact_info = 'show_contact_info' in request.POST
        privacy.show_connect_list = 'show_connect_list' in request.POST
        privacy.save()
        messages.success(request, "Privacy settings updated.")
        return redirect('accounts:profile', username=request.user.username)

    return render(request, 'accounts/privacy_settings.html', {'privacy': privacy})










def base_view(request):
    return render(request, 'base.html')


    
def alumni_view(request):
    return render(request, 'accounts/alumni.html')



from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.conf import settings
from .models import CustomUser
import random

# Temporary in-memory store for OTPs
OTP_STORE = {}

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "No user found with this email.")
            return redirect('accounts:forgot_password')

        # Generate OTP
        otp = random.randint(100000, 999999)
        OTP_STORE[email] = otp

        # Send OTP email
        subject = "College Connect - Password Reset OTP"
        message = f"Your OTP for password reset is {otp}."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        return render(request, 'accounts/forgot_password.html', {'otp_sent': True, 'email': email})

    return render(request, 'accounts/forgot_password.html', {'otp_sent': False})


def verify_otp(request):
    if request.method == "POST":
        email = request.POST.get('email')
        otp_entered = request.POST.get('otp')

        if email in OTP_STORE and str(OTP_STORE[email]) == otp_entered:
            del OTP_STORE[email]  # Remove OTP after successful verification
            request.session['reset_email'] = email
            return redirect('accounts:reset_password')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'accounts/forgot.html', {'otp_sent': True, 'email': email})

    return redirect('accounts:forgot_password')


def reset_password(request):
    email = request.session.get('reset_email')

    if not email:
        messages.error(request, "Session expired. Please request a new OTP.")
        return redirect('accounts:forgot_password')

    if request.method == "POST":
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/reset_password.html')

        user = CustomUser.objects.get(email=email)
        user.password = make_password(password1)
        user.save()

        del request.session['reset_email']
        messages.success(request, "Password reset successfully! Please log in.")
        return redirect('accounts:login')

    return render(request, 'accounts/reset_password.html')

@login_required
def live_search_posts(request):
    query = request.GET.get('q', '')
    posts = Post.objects.exclude(author=request.user)

    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(description__icontains=query))

    for post in posts:
        post.is_liked = Like.objects.filter(post=post, user=request.user).exists()
        post.likes_count = Like.objects.filter(post=post).count()
        post.comments_count = Comment.objects.filter(post=post).count()

        try:
            url = post.get_absolute_url()
            post.full_url = request.build_absolute_uri(url)
        except:
            post.full_url = ""

    html = render_to_string('partials/post_list.html', {'posts': posts}, request=request)
    return HttpResponse(html)




def post_comments(request, post_id):
    page = request.GET.get("page", 1)

    comments = Comment.objects.filter(post_id=post_id).order_by("-created_at")
    paginator = Paginator(comments, 5)

    page_obj = paginator.get_page(page)

    comments_data = []
    for c in page_obj:
        comments_data.append({
            "user": c.user.username,
            "pic": c.user.profile_pic.url if hasattr(c.user, "profile_pic") and c.user.profile_pic else None,
            "text": c.content,
            "time": c.created_at.strftime("%d %b %Y, %I:%M %p")
        })

    return JsonResponse({"comments": comments_data, "has_next": page_obj.has_next()})



#admin delete user
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from accounts.models import CustomUser

@user_passes_test(lambda u: u.is_superuser)
def admin_delete_users(request):
    users = CustomUser.objects.all().exclude(is_superuser=True)
    return render(request, "admin/delete_users.html", {"users": users})

#admin delete search
@user_passes_test(lambda u: u.is_superuser)
def search_users(request):
    q = request.GET.get("q", "")

    users = CustomUser.objects.filter(
        Q(username__icontains=q) |
        Q(current_designation__icontains=q) |
        Q(department__icontains=q) |
        Q(batch__icontains=q)
    ).exclude(is_superuser=True)

    return render(request, "admin/partials/user_cards.html", {"users": users})

#admin delete users
@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, uid):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"})
    
    user = get_object_or_404(CustomUser, id=uid)
    user.delete()
    
    return JsonResponse({"success": True})

