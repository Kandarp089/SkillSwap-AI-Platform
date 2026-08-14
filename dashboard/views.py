from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from skills.models import Skill
from exchanges.models import ExchangeRequest

User = get_user_model()

def dashboard_home(request):
    skills_count = Skill.objects.count()
    exchanges_count = ExchangeRequest.objects.count()
    users_count = User.objects.count()

    recent_exchanges = []
    if request.user.is_authenticated:
        recent_exchanges = ExchangeRequest.objects.filter(
            receiver=request.user
        ).order_by('-created_at')[:5]

    return render(request, 'dashboard/dashboard.html', {
        "skills_count": skills_count,
        "exchanges_count": exchanges_count,
        "users_count": users_count,
        "recent_exchanges": recent_exchanges
    })

def leaderboard(request):
    users = User.objects.select_related('profile').all()[:10]
    return render(request, 'dashboard/leaderboard.html', {"users": users})

def notifications(request):
    return render(request, "dashboard/notifications.html")

def settings_page(request):
    return render(request, "dashboard/settings.html")

def achievements(request):
    return render(request, "dashboard/achievements.html")

def certificates(request):
    return render(request, "dashboard/certificates.html")

def community(request):
    return render(request, 'dashboard/community.html')

def events(request):
    return render(request, 'dashboard/events.html')

def about(request):
    return render(request, 'dashboard/about.html')

def contact(request):
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