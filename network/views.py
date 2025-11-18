# network/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from accounts.models import Connection
import random
from django.db.models import Q 
from django.template.loader import render_to_string
from django.http import HttpResponse

User = get_user_model()

@login_required
def alumni_directory(request):
    all_users = User.objects.exclude(id=request.user.id)
    query = request.GET.get("q")

    if query:
        all_users = all_users.filter(
            Q(username__icontains=query) |
            Q(current_designation__icontains=query) |
            Q(company__icontains=query) |
            Q(location__icontains=query)
        ).distinct()

    if request.GET.get("ajax"):
        html = render_to_string("partials/search_users.html", {"users": all_users})
        return HttpResponse(html)

    # Get connections where the current user is either sender or receiver
    sent_connections = Connection.objects.filter(from_user=request.user)
    received_connections = Connection.objects.filter(to_user=request.user)

    all_connections = list(sent_connections) + list(received_connections)

    connection_map = {}
    for conn in all_connections:
        other_user = conn.to_user if conn.from_user == request.user else conn.from_user
        connection_map[other_user.id] = conn

    users_to_display = list(all_users)
    for user in users_to_display:
        user.connection = connection_map.get(user.id, None)

        if hasattr(user, "profile_pic") and user.profile_pic:
            user.profile_pic_url = user.profile_pic.url
        else:
            user.profile_pic_url = "https://via.placeholder.com/150"

        if not getattr(user, "designation", None):
            user.designation = "Student"
        if not getattr(user, "company", None):
            user.company = ""

    random.shuffle(users_to_display)

    return render(request, 'network/network.html', {
        'users': users_to_display,
    })


@login_required
def live_search_users(request):
    query = request.GET.get('q', '')
    users = User.objects.exclude(id=request.user.id)

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(current_designation__icontains=query) |
            Q(company__icontains=query)
        )

    for u in users:
        u.profile_pic_url = (
            u.profile_pic.url if getattr(u, "profile_pic", None) and u.profile_pic else "https://via.placeholder.com/150"
        )

    html = render_to_string('partials/user_list.html', {'users': users})
    return HttpResponse(html)
