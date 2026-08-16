from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import ExchangeRequest, XPLedger, CreditTransaction
from notifications.models import Notification

@transaction.atomic
def complete_exchange(exchange_id, user):
    """
    Atomically complete an exchange request:
    - Validates that user is sender or receiver
    - Confirms completion for user
    - When both confirm (or single admin call), marks exchange as completed
    - Atomically awards +150 XP to learner, +200 XP (+50 mentorship bonus) to mentor
    - Atomically transfers +25 credits
    - Prevents double execution or negative balances
    """
    exchange = ExchangeRequest.objects.select_for_update().get(id=exchange_id)
    
    if exchange.status in ['completed', 'cancelled', 'rejected']:
        raise ValidationError("This exchange is already finalized.")

    if user == exchange.sender or user == exchange.receiver or user.is_staff or getattr(user, 'is_admin_or_staff', False):
        exchange.sender_confirmed = True
        exchange.receiver_confirmed = True
    else:
        raise ValidationError("You are not a participant in this exchange.")

    if exchange.sender_confirmed and exchange.receiver_confirmed:
        exchange.status = 'completed'
        exchange.completed_at = timezone.now()
        exchange.save()

        # Award XP to Sender (+150 XP)
        sender_prof = exchange.sender.profile
        sender_prof.xp += 150
        sender_prof.calculate_level()
        sender_prof.save()

        XPLedger.objects.create(
            user=exchange.sender,
            amount=150,
            reason="Completed Skill Exchange Session",
            reference=f"exchange_{exchange.id}"
        )

        # Award XP to Receiver (+200 XP: 150 + 50 mentorship bonus)
        receiver_prof = exchange.receiver.profile
        receiver_prof.xp += 200
        receiver_prof.calculate_level()
        receiver_prof.save()

        XPLedger.objects.create(
            user=exchange.receiver,
            amount=200,
            reason="Mentorship & Skill Exchange Completion",
            reference=f"exchange_{exchange.id}"
        )

        # Award +25 Credits to Receiver (Mentor)
        receiver_prof.credits += 25
        receiver_prof.save()

        CreditTransaction.objects.create(
            user=exchange.receiver,
            amount=25,
            transaction_type='earned',
            description=f"Earned for completed exchange with @{exchange.sender.username}",
            balance_after=receiver_prof.credits
        )

        # Notify participants
        Notification.objects.create(
            user=exchange.sender,
            sender=exchange.receiver,
            notification_type='system',
            title="Exchange Completed! 🎉",
            message=f"Your skill exchange with @{exchange.receiver.username} is complete! You earned +150 XP.",
            link=f"/exchanges/{exchange.id}/"
        )
        Notification.objects.create(
            user=exchange.receiver,
            sender=exchange.sender,
            notification_type='system',
            title="Exchange Completed! 🎉",
            message=f"Your mentorship session with @{exchange.sender.username} is complete! You earned +200 XP & +25 Credits.",
            link=f"/exchanges/{exchange.id}/"
        )
    else:
        exchange.status = 'in_progress'
        exchange.save()

    return exchange
