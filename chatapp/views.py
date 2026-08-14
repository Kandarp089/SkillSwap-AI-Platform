from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

@login_required(login_url='accounts:login')
def chat_home(request):
    messages_qs = Message.objects.filter(sender=request.user) | Message.objects.filter(receiver=request.user)
    messages_qs = messages_qs.select_related('sender', 'receiver').order_by('created_at')
    
    other_users = User.objects.exclude(id=request.user.id)
    return render(request, "chatapp/chat.html", {
        "db_messages": messages_qs,
        "other_users": other_users
    })

@login_required(login_url='accounts:login')
def send_message(request):
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        msg_text = request.POST.get("message", "").strip()

        if msg_text:
            receiver = User.objects.filter(id=receiver_id).first() if receiver_id else User.objects.exclude(id=request.user.id).first()
            if receiver:
                new_msg = Message.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    message=msg_text
                )
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        "status": "success",
                        "id": new_msg.id,
                        "sender": new_msg.sender.username,
                        "message": new_msg.message,
                        "created_at": new_msg.created_at.strftime("%I:%M %p")
                    })
    return redirect("chatapp:chat")