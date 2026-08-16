from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Message, Conversation, ConversationMember
from notifications.models import Notification

User = get_user_model()

@login_required(login_url='accounts:login')
def chat_home(request):
    target_username = request.GET.get('user', '').strip()
    other_users = User.objects.exclude(id=request.user.id).select_related('profile')

    active_partner = None
    if target_username:
        active_partner = User.objects.filter(username__iexact=target_username).first()
    
    if not active_partner and other_users.exists():
        active_partner = other_users.first()

    messages_qs = Message.objects.none()
    room_name = ""

    if active_partner:
        # Canonical room name using user handles sorted alphabetically
        user_handles = sorted([request.user.username.lower(), active_partner.username.lower()])
        room_name = f"{user_handles[0]}_{user_handles[1]}"

        # Query messages between request.user and active_partner
        messages_qs = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=active_partner)) |
            (Q(sender=active_partner) & Q(receiver=request.user))
        ).select_related('sender', 'receiver').order_by('created_at')

        # Mark unread messages as read
        Message.objects.filter(sender=active_partner, receiver=request.user, is_read=False).update(is_read=True)

    return render(request, "chatapp/chat.html", {
        "active_partner": active_partner,
        "other_users": other_users,
        "messages": messages_qs,
        "room_name": room_name,
    })


@login_required(login_url='accounts:login')
def send_message(request):
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        receiver_username = request.POST.get("receiver_username")
        msg_text = request.POST.get("message", "").strip()

        receiver = None
        if receiver_id:
            receiver = User.objects.filter(id=receiver_id).first()
        elif receiver_username:
            receiver = User.objects.filter(username__iexact=receiver_username).first()

        if msg_text and receiver and receiver != request.user:
            new_msg = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                message=msg_text
            )

            Notification.objects.create(
                user=receiver,
                sender=request.user,
                notification_type='new_message',
                title=f"New message from {request.user.username}",
                message=msg_text[:100],
                link=f"/chat/?user={request.user.username}"
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    "status": "success",
                    "id": new_msg.id,
                    "sender": new_msg.sender.username,
                    "message": new_msg.message,
                    "created_at": new_msg.created_at.strftime("%I:%M %p")
                })
            
            return redirect(f"/chat/?user={receiver.username}")

    return redirect("chatapp:chat")