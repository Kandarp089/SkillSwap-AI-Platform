from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from skills.models import Skill
from exchanges.models import ExchangeRequest
from .models import Notification, Achievement, UserAchievement, Certificate, CommunityPost, Event

User = get_user_model()

@login_required(login_url='accounts:login')
def dashboard_home(request):
    user = request.user
    profile = getattr(user, 'profile', None)

    active_swaps_count = ExchangeRequest.objects.filter(
        (Q(sender=user) | Q(receiver=user)) & Q(status='accepted')
    ).count()

    pending_requests = ExchangeRequest.objects.filter(receiver=user, status='pending').select_related('sender', 'sender__profile').order_by('-created_at')[:5]
    sent_pending_requests = ExchangeRequest.objects.filter(sender=user, status='pending').select_related('receiver', 'receiver__profile').order_by('-created_at')[:5]

    accepted_sessions = ExchangeRequest.objects.filter(
        (Q(sender=user) | Q(receiver=user)) & Q(status='accepted')
    ).select_related('sender', 'receiver', 'sender__profile', 'receiver__profile').order_by('-updated_at')[:5]

    total_skills_count = Skill.objects.filter(user=user).count()
    total_platform_skills = Skill.objects.count()

    return render(request, 'dashboard/dashboard.html', {
        "user_profile": profile,
        "active_swaps_count": active_swaps_count,
        "pending_requests": pending_requests,
        "sent_pending_requests": sent_pending_requests,
        "accepted_sessions": accepted_sessions,
        "total_skills_count": total_skills_count,
        "total_platform_skills": total_platform_skills,
    })

def leaderboard(request):
    period = request.GET.get('period', 'all')
    users_qs = User.objects.select_related('profile').all()

    if period == 'monthly':
        users = sorted(users_qs, key=lambda u: getattr(u, 'profile', None).xp if getattr(u, 'profile', None) else 0, reverse=True)[:10]
    else:
        users = sorted(users_qs, key=lambda u: getattr(u, 'profile', None).xp if getattr(u, 'profile', None) else 0, reverse=True)[:15]

    return render(request, 'dashboard/leaderboard.html', {
        "leaderboard_users": users,
        "selected_period": period
    })

@login_required(login_url='accounts:login')
def notifications(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "mark_all_read":
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            messages.success(request, "All notifications marked as read.")
            return redirect("dashboard:notifications")
        elif action == "mark_read":
            notif_id = request.POST.get("notif_id")
            if notif_id:
                Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
                return redirect("dashboard:notifications")

    user_notifications = Notification.objects.filter(user=request.user).select_related('sender').order_by('-created_at')
    return render(request, "dashboard/notifications.html", {
        "notifications": user_notifications
    })

def settings_page(request):
    return render(request, "dashboard/settings.html")

def seed_achievements_if_empty():
    if Achievement.objects.count() == 0:
        Achievement.objects.create(title="First Skill Exchange", description="Completed your very first peer skill swap session.", icon="bi-rocket-takeoff", badge_color="purple", criteria="1_exchange", xp_reward=100)
        Achievement.objects.create(title="Top Peer Mentor", description="Received 5-star ratings across 5 consecutive exchanges.", icon="bi-star-fill", badge_color="gold", criteria="5_stars", xp_reward=300)
        Achievement.objects.create(title="Skill Master", description="Published 3 distinct skills for teaching.", icon="bi-award-fill", badge_color="cyan", criteria="3_skills", xp_reward=200)
        Achievement.objects.create(title="Community Pioneer", description="Joined SkillSwap AI early release cohort.", icon="bi-shield-check", badge_color="emerald", criteria="early_member", xp_reward=150)

def achievements(request):
    seed_achievements_if_empty()
    all_achievements = Achievement.objects.all()

    unlocked_ids = []
    if request.user.is_authenticated:
        unlocked_ids = list(UserAchievement.objects.filter(user=request.user).values_list('achievement_id', flat=True))
        # Award 'First Skill Exchange' if completed exchange exists but achievement not logged
        completed = ExchangeRequest.objects.filter((Q(sender=request.user) | Q(receiver=request.user)) & Q(status='completed')).exists()
        if completed:
            first_ach = Achievement.objects.filter(title="First Skill Exchange").first()
            if first_ach and first_ach.id not in unlocked_ids:
                UserAchievement.objects.get_or_create(user=request.user, achievement=first_ach)
                unlocked_ids.append(first_ach.id)

    return render(request, "dashboard/achievements.html", {
        "achievements": all_achievements,
        "unlocked_ids": unlocked_ids,
    })

def certificates(request):
    user_certs = []
    if request.user.is_authenticated:
        user_certs = Certificate.objects.filter(user=request.user).order_by('-issued_date')
        if not user_certs.exists():
            # Create default demo certificate for user
            Certificate.objects.create(
                certificate_id=f"CERT-{request.user.id}-PY2026",
                user=request.user,
                skill_title="Python & Django Web Architecture",
                achievement_title="Verified Peer Mentorship Certificate"
            )
            user_certs = Certificate.objects.filter(user=request.user)

    return render(request, "dashboard/certificates.html", {
        "certificates": user_certs
    })

def community(request):
    if request.method == "POST" and request.user.is_authenticated:
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        category = request.POST.get("category", "General")

        if title and content:
            CommunityPost.objects.create(
                author=request.user,
                title=title,
                content=content,
                category=category
            )
            messages.success(request, "Community discussion post published!")
            return redirect("dashboard:community")

    posts = CommunityPost.objects.select_related('author', 'author__profile').order_by('-created_at')
    return render(request, 'dashboard/community.html', {
        "posts": posts
    })

def events(request):
    if request.method == "POST" and request.user.is_authenticated:
        event_id = request.POST.get("event_id")
        if event_id:
            event = Event.objects.filter(id=event_id).first()
            if event:
                event.attendees_count += 1
                event.save(update_fields=['attendees_count'])
                messages.success(request, f"RSVP Confirmed for '{event.title}'! Link added to your calendar.")
                return redirect("dashboard:events")

    events_list = Event.objects.select_related('organizer').order_by('event_date')
    return render(request, 'dashboard/events.html', {
        "events": events_list
    })

def about(request):
    return render(request, 'dashboard/about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        if name and email and message_text:
            messages.success(request, f"Thank you {name}! Your message has been received. Our team will get back to you shortly.")
            return redirect("dashboard:contact")
        else:
            messages.error(request, "Please complete all required fields in the contact form.")

    return render(request, 'dashboard/contact.html')

def help_center(request):
    return render(request, 'dashboard/help_center.html')

def blog(request):
    return render(request, 'dashboard/blog.html')

def careers(request):
    return render(request, 'dashboard/careers.html')

def privacy_policy(request):
    return render(request, 'dashboard/privacy_policy.html')

def terms_of_use(request):
    return render(request, 'dashboard/terms_of_use.html')

def cookies_policy(request):
    return render(request, 'dashboard/cookies_policy.html')

def accessibility(request):
    return render(request, 'dashboard/accessibility.html')