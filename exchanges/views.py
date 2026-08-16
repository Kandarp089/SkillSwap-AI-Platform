from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from .models import ExchangeRequest
from notifications.models import Notification
from .services import complete_exchange

User = get_user_model()

@login_required(login_url='accounts:login')
def send_request(request):
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        receiver_username = request.POST.get("receiver_username")
        offered_skill = request.POST.get("offered_skill", "Python Development").strip()
        requested_skill = request.POST.get("requested_skill", "UI/UX Design").strip()
        note = request.POST.get("note", "").strip()

        receiver = None
        if receiver_id:
            receiver = User.objects.filter(id=receiver_id).first()
        elif receiver_username:
            receiver = User.objects.filter(username__iexact=receiver_username).first()

        if not receiver:
            receiver = User.objects.exclude(id=request.user.id).first()

        if receiver and receiver != request.user:
            existing = ExchangeRequest.objects.filter(
                sender=request.user,
                receiver=receiver,
                status='pending'
            ).first()

            if existing:
                messages.info(request, f"You already have a pending swap proposal with {receiver.username}.")
                return redirect("exchanges:my_exchanges")

            ex_req = ExchangeRequest.objects.create(
                sender=request.user,
                receiver=receiver,
                offered_skill=offered_skill,
                requested_skill=requested_skill,
                note=note,
                status='pending'
            )

            Notification.objects.create(
                user=receiver,
                sender=request.user,
                notification_type='exchange_request',
                title=f"New Skill Swap Proposal from {request.user.username}",
                message=f"Wants to learn '{requested_skill}' in exchange for '{offered_skill}'.",
                link="/requests/my-exchanges/"
            )

            messages.success(request, f"Skill Swap proposal sent to {receiver.username}!")
        else:
            messages.error(request, "Invalid receiver for skill swap request.")

        return redirect("exchanges:my_exchanges")
    return redirect("exchanges:my_exchanges")


@login_required(login_url='accounts:login')
def requests_page(request):
    received = ExchangeRequest.objects.filter(receiver=request.user).select_related('sender', 'sender__profile').order_by('-created_at')
    sent = ExchangeRequest.objects.filter(sender=request.user).select_related('receiver', 'receiver__profile').order_by('-created_at')
    return render(request, "exchanges/requests.html", {
        "received_requests": received,
        "sent_requests": sent
    })


@login_required(login_url='accounts:login')
def accept_request(request, request_id):
    ex_req = get_object_or_404(ExchangeRequest, id=request_id)
    if ex_req.receiver == request.user and ex_req.status == 'pending':
        ex_req.status = 'accepted'
        ex_req.save()

        Notification.objects.create(
            user=ex_req.sender,
            sender=request.user,
            notification_type='request_accepted',
            title=f"Swap Request Accepted!",
            message=f"{request.user.username} accepted your skill swap for '{ex_req.requested_skill}'.",
            link=f"/chat/?user={request.user.username}"
        )

        messages.success(request, f"Accepted swap proposal from {ex_req.sender.username}! You can now start chatting.")
    return redirect("exchanges:my_exchanges")


@login_required(login_url='accounts:login')
def reject_request(request, request_id):
    ex_req = get_object_or_404(ExchangeRequest, id=request_id)
    if ex_req.receiver == request.user and ex_req.status == 'pending':
        ex_req.status = 'rejected'
        ex_req.save()

        Notification.objects.create(
            user=ex_req.sender,
            sender=request.user,
            notification_type='request_rejected',
            title=f"Swap Request Declined",
            message=f"{request.user.username} declined your skill swap proposal.",
            link="/requests/my-exchanges/"
        )

        messages.info(request, f"Declined swap proposal from {ex_req.sender.username}.")
    return redirect("exchanges:my_exchanges")


@login_required(login_url='accounts:login')
def complete_request(request, request_id):
    try:
        complete_exchange(request_id, request.user)
        messages.success(request, "Skill Swap marked as completed! +150 XP & Credits awarded!")
    except Exception as e:
        messages.error(request, str(e))
    return redirect("exchanges:my_exchanges")


@login_required(login_url='accounts:login')
def cancel_request(request, request_id):
    ex_req = get_object_or_404(ExchangeRequest, id=request_id)
    if ex_req.sender == request.user and ex_req.status == 'pending':
        ex_req.status = 'cancelled'
        ex_req.save()
        messages.info(request, "Swap request cancelled.")
    return redirect("exchanges:my_exchanges")


@login_required(login_url='accounts:login')
def my_exchanges(request):
    exchanges = ExchangeRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver', 'sender__profile', 'receiver__profile').order_by('-created_at')

    return render(request, "exchanges/my_exchanges.html", {
        "exchanges": exchanges
    })