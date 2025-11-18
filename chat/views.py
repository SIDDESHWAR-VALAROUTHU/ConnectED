# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.db.models import Q
from accounts.models import Connection, CustomUser  # your models
from .models import Message
from django.utils import timezone

@login_required
def chat_home(request):
    user = request.user
    connected_users = CustomUser.objects.filter(
        Q(sent_requests__to_user=user, sent_requests__status='accepted') |
        Q(received_requests__from_user=user, received_requests__status='accepted')
    ).distinct()

    # pick first connected user (if any) to pre-select
    selected_user = connected_users.first() if connected_users.exists() else None

    messages = []
    if selected_user:
        messages = Message.objects.filter(
            (Q(sender=user, receiver=selected_user)) | (Q(sender=selected_user, receiver=user))
        ).order_by('timestamp')

    return render(request, 'chat/pro_chat.html', {
        'connected_users': connected_users,
        'selected_user': selected_user,
        'messages': messages,
    })

@login_required
def chat_with(request, username):
    user = request.user
    selected_user = get_object_or_404(CustomUser, username=username)

    connected_users = CustomUser.objects.filter(
        Q(sent_requests__to_user=user, sent_requests__status='accepted') |
        Q(received_requests__from_user=user, received_requests__status='accepted')
    ).distinct()

    # enforce only connected users allowed
    if selected_user not in connected_users:
        return redirect('chat:chat_home')

    # GET -> show page with messages
    if request.method == 'GET':
        messages = Message.objects.filter(
            (Q(sender=user, receiver=selected_user)) | (Q(sender=selected_user, receiver=user))
        ).order_by('timestamp')
        return render(request, 'chat/pro_chat.html', {
            'connected_users': connected_users,
            'selected_user': selected_user,
            'messages': messages,
        })

    # POST -> sending message (AJAX-friendly)
    if request.method == 'POST':
        content = request.POST.get('message') or request.body and request.POST.get('message')
        if not content:
            # support JSON body as well
            import json
            try:
                data = json.loads(request.body.decode())
                content = data.get('message')
            except Exception:
                pass

        if not content:
            return HttpResponseBadRequest("Empty message")

        msg = Message.objects.create(sender=user, receiver=selected_user, content=content)
        # Optionally: return JSON when AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'id': msg.id,
                'sender': user.username,
                'message': msg.content,
                'timestamp': msg.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            })
        return redirect('chat:chat_with', username=username)

@login_required
def fetch_messages(request, username):
    """Return JSON list of messages between request.user and username.
       Accepts ?after=<ISO timestamp> to fetch only newer messages.
    """
    user = request.user
    other = get_object_or_404(CustomUser, username=username)

    # ensure connected
    connected_users = CustomUser.objects.filter(
        Q(sent_requests__to_user=user, sent_requests__status='accepted') |
        Q(received_requests__from_user=user, received_requests__status='accepted')
    ).distinct()
    if other not in connected_users:
        return JsonResponse({'error': 'not connected'}, status=403)

    after = request.GET.get('after')
    qs = Message.objects.filter(
        (Q(sender=user, receiver=other)) | (Q(sender=other, receiver=user))
    ).order_by('timestamp')
    if after:
        # parse ISO-ish timestamp
        try:
            from django.utils.dateparse import parse_datetime
            dt = parse_datetime(after)
            if dt is not None:
                qs = qs.filter(timestamp__gt=dt)
        except Exception:
            pass

    msgs = []
    for m in qs:
        msgs.append({
            'id': m.id,
            'sender': m.sender.username,
            'receiver': m.receiver.username,
            'content': m.content,
            'timestamp': m.timestamp.isoformat(),
        })
    return JsonResponse({'messages': msgs})
