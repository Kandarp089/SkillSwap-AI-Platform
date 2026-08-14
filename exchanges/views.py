from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import ExchangeRequest

User = get_user_model()

@login_required(login_url='accounts:login')
def send_request(request):
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        offered_skill = request.POST.get("offered_skill", "Python Development")
        requested_skill = request.POST.get("requested_skill", "UI/UX Design")
        note = request.POST.get("note", "")

        receiver = User.objects.filter(id=receiver_id).first() if receiver_id else User.objects.exclude(id=request.user.id).first()

        if receiver and receiver != request.user:
            req = ExchangeRequest.objects.create(
                sender=request.user,
                receiver=receiver,
                offered_skill=offered_skill,
                requested_skill=requested_skill,
                note=note,
                status='pending'
            )
            messages.success(request, f"Skill Swap proposal sent to {receiver.username}!")
        else:
            messages.info(request, "Skill Swap proposal created successfully!")
            
        return redirect("exchanges:my_exchanges")
    return redirect("exchanges:my_exchanges")

@login_required(login_url='accounts:login')
def requests_page(request):
    received = ExchangeRequest.objects.filter(receiver=request.user).order_by('-created_at')
    sent = ExchangeRequest.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, "exchanges/requests.html", {
        "received_requests": received,
        "sent_requests": sent
    })

@login_required(login_url='accounts:login')
def accept_request(request, request_id):
    ex_req = get_object_or_404(ExchangeRequest, id=request_id)
    if ex_req.receiver == request.user:
        ex_req.status = 'accepted'
        ex_req.save()
        messages.success(request, f"Accepted swap proposal from {ex_req.sender.username}!")
    return redirect("exchanges:my_exchanges")

@login_required(login_url='accounts:login')
def reject_request(request, request_id):
    ex_req = get_object_or_404(ExchangeRequest, id=request_id)
    if ex_req.receiver == request.user:
        ex_req.status = 'rejected'
        ex_req.save()
        messages.info(request, f"Declined swap proposal from {ex_req.sender.username}.")
    return redirect("exchanges:my_exchanges")

@login_required(login_url='accounts:login')
def my_exchanges(request):
    exchanges = ExchangeRequest.objects.filter(sender=request.user) | ExchangeRequest.objects.filter(receiver=request.user)
    exchanges = exchanges.order_by('-created_at')
    return render(request, "exchanges/my_exchanges.html", {
        "exchanges": exchanges
    })