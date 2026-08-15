from dashboard.models import Notification
from exchanges.models import ExchangeRequest

def site_context(request):
    unread_notifications_count = 0
    pending_requests_count = 0
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        pending_requests_count = ExchangeRequest.objects.filter(receiver=request.user, status='pending').count()

    return {
        "site_name": "SkillSwap AI",
        "unread_notifications_count": unread_notifications_count,
        "pending_requests_count": pending_requests_count,
    }