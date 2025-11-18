from .models import Connection

def pending_request_count(request):
    """Adds pending request count and preview list to all templates."""
    if request.user.is_authenticated:
        pending_requests = Connection.objects.filter(
            to_user=request.user, status='pending'
        ).select_related('from_user')[:5]  # limit to latest 5
        return {
            'pending_request_count': pending_requests.count(),
            'pending_requests': pending_requests,
        }
    return {}
